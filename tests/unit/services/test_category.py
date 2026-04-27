"""
Unit tests for CategoryService
"""

import pytest
from src.services.category_service import CategoryService
from src.services.auth_service import AuthService
from src.models.category import Category
from src.models.user import User
from src.models.source import Source
from src.models.transaction import Transaction
from src.models.budget import Budget
from src.utils.exceptions import ValidationError, NotFoundError, AlreadyExistsError


# ============= Fixtures =============

@pytest.fixture
def db_session(tmp_path):
    """Create a temporary database for testing"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.config.database import Base

    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    auth_service = AuthService(db_session)
    user = auth_service.register_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    return user


@pytest.fixture
def category_service(db_session):
    """Create a CategoryService instance"""
    return CategoryService(db_session)


# ============= Create Category Tests =============

@pytest.mark.unit
class TestCreateCategory:
    """Tests for creating categories"""

    def test_create_basic_category(self, category_service, test_user):
        """Test creating a basic category"""
        category = category_service.create_category(
            user_id=test_user.id,
            name="Groceries",
            category_type="expense",
        )

        assert category.id is not None
        assert category.user_id == test_user.id
        assert category.name == "Groceries"
        assert category.category_type == "expense"
        assert category.is_system is False

    def test_create_category_with_parent(self, category_service, test_user):
        """Test creating a category with parent"""
        parent = category_service.create_category(
            test_user.id, "Shopping", "expense"
        )
        child = category_service.create_category(
            test_user.id, "Groceries", "expense", parent_id=parent.id
        )

        assert child.parent_id == parent.id

    def test_create_category_with_matching_pattern(self, category_service, test_user):
        """Test creating category with matching pattern"""
        category = category_service.create_category(
            test_user.id,
            "Gas Stations",
            "expense",
            matching_pattern="(?i)(shell|chevron|mobil|bp)",
        )

        assert category.matching_pattern is not None

    def test_create_category_empty_name_raises_error(self, category_service, test_user):
        """Test that empty name raises ValidationError"""
        with pytest.raises(ValidationError, match="Name cannot be empty"):
            category_service.create_category(
                test_user.id, "", "expense"
            )

    def test_create_category_invalid_type_raises_error(self, category_service, test_user):
        """Test that invalid category_type raises ValidationError"""
        with pytest.raises(ValidationError, match="Invalid category_type"):
            category_service.create_category(
                test_user.id, "Test", "invalid_type"
            )

    def test_create_category_duplicate_name_raises_error(self, category_service, test_user):
        """Test that duplicate name raises AlreadyExistsError"""
        category_service.create_category(test_user.id, "Groceries", "expense")

        with pytest.raises(AlreadyExistsError, match="already exists"):
            category_service.create_category(test_user.id, "Groceries", "expense")

    def test_create_category_parent_not_found_raises_error(self, category_service, test_user):
        """Test that invalid parent_id raises NotFoundError"""
        with pytest.raises(NotFoundError, match="Parent category"):
            category_service.create_category(
                test_user.id, "Test", "expense", parent_id=99999
            )

    def test_create_category_parent_type_mismatch_raises_error(self, category_service, test_user):
        """Test that parent with different type raises ValidationError"""
        parent = category_service.create_category(test_user.id, "Salary", "income")

        with pytest.raises(ValidationError, match="same type"):
            category_service.create_category(
                test_user.id, "Food", "expense", parent_id=parent.id
            )


# ============= Get Category Tests =============

@pytest.mark.unit
class TestGetCategory:
    """Tests for getting categories"""

    def test_get_category_by_id(self, category_service, test_user):
        """Test getting a category by ID"""
        created = category_service.create_category(
            test_user.id, "Test", "expense"
        )

        category = category_service.get_category(created.id, test_user.id)

        assert category is not None
        assert category.id == created.id

    def test_get_nonexistent_category_returns_none(self, category_service, test_user):
        """Test that getting nonexistent category returns None"""
        category = category_service.get_category(99999, test_user.id)
        assert category is None


# ============= List Categories Tests =============

@pytest.mark.unit
class TestListCategories:
    """Tests for listing categories"""

    def test_list_user_categories(self, category_service, test_user):
        """Test listing all categories for user"""
        category_service.create_category(test_user.id, "Cat1", "expense")
        category_service.create_category(test_user.id, "Cat2", "expense")
        category_service.create_category(test_user.id, "Cat3", "income")

        categories = category_service.list_categories(test_user.id)

        assert len(categories) == 3

    def test_list_categories_by_type(self, category_service, test_user):
        """Test filtering categories by type"""
        category_service.create_category(test_user.id, "Food", "expense")
        category_service.create_category(test_user.id, "Salary", "income")
        category_service.create_category(test_user.id, "Bonus", "income")

        income_cats = category_service.list_categories(
            test_user.id, category_type="income"
        )

        assert len(income_cats) == 2
        assert all(c.category_type == "income" for c in income_cats)

    def test_list_root_categories_only(self, category_service, test_user):
        """Test listing only root categories"""
        parent = category_service.create_category(test_user.id, "Parent", "expense")
        category_service.create_category(test_user.id, "Child", "expense", parent_id=parent.id)

        roots = category_service.list_categories(
            test_user.id, include_subcategories=False
        )

        assert len(roots) == 1
        assert roots[0].name == "Parent"

    def test_list_categories_sorted_by_name(self, category_service, test_user):
        """Test that categories are sorted alphabetically"""
        category_service.create_category(test_user.id, "Zebra", "expense")
        category_service.create_category(test_user.id, "Alpha", "expense")
        category_service.create_category(test_user.id, "Beta", "expense")

        categories = category_service.list_categories(test_user.id)

        assert categories[0].name == "Alpha"
        assert categories[1].name == "Beta"
        assert categories[2].name == "Zebra"


# ============= Category Hierarchy Tests =============

@pytest.mark.unit
class TestCategoryHierarchy:
    """Tests for category hierarchy operations"""

    def test_get_category_hierarchy(self, category_service, test_user):
        """Test getting full category hierarchy"""
        parent = category_service.create_category(test_user.id, "Parent", "expense")
        child1 = category_service.create_category(
            test_user.id, "Child1", "expense", parent_id=parent.id
        )
        child2 = category_service.create_category(
            test_user.id, "Child2", "expense", parent_id=parent.id
        )
        grandchild = category_service.create_category(
            test_user.id, "Grandchild", "expense", parent_id=child1.id
        )

        hierarchy = category_service.get_category_hierarchy(parent.id, test_user.id)

        assert len(hierarchy) == 4
        assert parent in hierarchy
        assert child1 in hierarchy
        assert child2 in hierarchy
        assert grandchild in hierarchy


# ============= Update Category Tests =============

@pytest.mark.unit
class TestUpdateCategory:
    """Tests for updating categories"""

    def test_update_category_name(self, category_service, test_user):
        """Test updating category name"""
        category = category_service.create_category(
            test_user.id, "Old Name", "expense"
        )

        updated = category_service.update_category(
            category.id, test_user.id, name="New Name"
        )

        assert updated.name == "New Name"

    def test_update_category_parent(self, category_service, test_user):
        """Test updating category parent"""
        parent = category_service.create_category(test_user.id, "Parent", "expense")
        category = category_service.create_category(test_user.id, "Child", "expense")

        updated = category_service.update_category(
            category.id, test_user.id, parent_id=parent.id
        )

        assert updated.parent_id == parent.id

    def test_update_nonexistent_category_raises_error(self, category_service, test_user):
        """Test that updating nonexistent category raises NotFoundError"""
        with pytest.raises(NotFoundError):
            category_service.update_category(99999, test_user.id, name="Test")

    def test_update_system_category_raises_error(self, category_service, test_user):
        """Test that updating system category raises ValidationError"""
        system_cat = category_service.create_category(
            test_user.id, "System", "expense", is_system=True
        )

        with pytest.raises(ValidationError, match="System categories"):
            category_service.update_category(system_cat.id, test_user.id, name="New")

    def test_update_category_circular_reference_raises_error(self, category_service, test_user):
        """Test that circular reference raises ValidationError"""
        parent = category_service.create_category(test_user.id, "Parent", "expense")
        child = category_service.create_category(
            test_user.id, "Child", "expense", parent_id=parent.id
        )

        with pytest.raises(ValidationError, match="circular"):
            category_service.update_category(
                parent.id, test_user.id, parent_id=child.id
            )


# ============= Delete Category Tests =============

@pytest.mark.unit
class TestDeleteCategory:
    """Tests for deleting categories"""

    def test_delete_category(self, category_service, test_user):
        """Test deleting a category"""
        category = category_service.create_category(test_user.id, "Test", "expense")

        result = category_service.delete_category(category.id, test_user.id)

        assert result is True
        assert category_service.get_category(category.id, test_user.id) is None

    def test_delete_nonexistent_category_raises_error(self, category_service, test_user):
        """Test that deleting nonexistent category raises NotFoundError"""
        with pytest.raises(NotFoundError):
            category_service.delete_category(99999, test_user.id)

    def test_delete_system_category_raises_error(self, category_service, test_user):
        """Test that deleting system category raises ValidationError"""
        system_cat = category_service.create_category(
            test_user.id, "System", "expense", is_system=True
        )

        with pytest.raises(ValidationError, match="System categories"):
            category_service.delete_category(system_cat.id, test_user.id)

    def test_delete_category_with_subcategories_raises_error(self, category_service, test_user):
        """Test that deleting category with subcategories raises ValidationError"""
        parent = category_service.create_category(test_user.id, "Parent", "expense")
        category_service.create_category(
            test_user.id, "Child", "expense", parent_id=parent.id
        )

        with pytest.raises(ValidationError, match="subcategories"):
            category_service.delete_category(parent.id, test_user.id)


# ============= Validation Tests =============

@pytest.mark.unit
class TestCategoryValidation:
    """Tests for category validation"""

    def test_valid_category_types(self, category_service, test_user):
        """Test all valid category types"""
        valid_types = ["expense", "income"]

        for cat_type in valid_types:
            category = category_service.create_category(
                test_user.id,
                f"Test {cat_type}",
                cat_type,
            )
            assert category.category_type == cat_type

    def test_name_max_length(self, category_service, test_user):
        """Test that name cannot exceed 100 characters"""
        with pytest.raises(ValidationError, match="cannot exceed 100 characters"):
            category_service.create_category(
                test_user.id,
                "A" * 101,
                "expense",
            )
