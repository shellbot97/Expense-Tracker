"""
Category service - Business logic for category management
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from src.models.category import Category
from src.utils.exceptions import ValidationError, NotFoundError, AlreadyExistsError


class CategoryService:
    """Service for managing expense/income categories"""

    VALID_CATEGORY_TYPES = ["expense", "income"]

    def __init__(self, db: Session):
        self.db = db

    def create_category(
        self,
        user_id: int,
        name: str,
        category_type: str,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
        matching_pattern: Optional[str] = None,
        is_system: bool = False,
        color: Optional[str] = None,
        icon: Optional[str] = None,
    ) -> Category:
        """
        Create a new category
        
        Args:
            user_id: User ID
            name: Category name
            category_type: Type (expense/income)
            description: Optional description
            parent_id: Parent category ID for hierarchy
            matching_pattern: Regex pattern for auto-categorization
            is_system: Whether this is a system category
            color: UI color (hex)
            icon: UI icon name
            
        Returns:
            Created category
            
        Raises:
            ValidationError: If validation fails
            AlreadyExistsError: If category name already exists for user
            NotFoundError: If parent_id doesn't exist
        """
        # Validate inputs
        self._validate_name(name)
        self._validate_category_type(category_type)
        
        # Check for duplicate name
        existing = self._get_category_by_name(user_id, name)
        if existing:
            raise AlreadyExistsError(f"Category with name '{name}' already exists")
        
        # Validate parent if provided
        if parent_id:
            parent = self.get_category(parent_id, user_id)
            if not parent:
                raise NotFoundError(f"Parent category with ID {parent_id} not found")
            # Ensure parent has same category_type
            if parent.category_type != category_type:
                raise ValidationError("Parent and child categories must have the same type")

        # Create category
        category = Category(
            user_id=user_id,
            name=name.strip(),
            category_type=category_type,
            description=description,
            parent_id=parent_id,
            matching_pattern=matching_pattern,
            is_system=is_system,
            color=color,
            icon=icon,
        )

        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        return category

    def get_category(self, category_id: int, user_id: int) -> Optional[Category]:
        """Get category by ID"""
        return (
            self.db.query(Category)
            .filter(
                Category.id == category_id,
                Category.user_id == user_id,
            )
            .first()
        )

    def list_categories(
        self,
        user_id: int,
        category_type: Optional[str] = None,
        parent_id: Optional[int] = None,
        is_system: Optional[bool] = None,
        include_subcategories: bool = True,
    ) -> List[Category]:
        """
        List categories for user with optional filters
        
        Args:
            user_id: User ID
            category_type: Filter by type (expense/income)
            parent_id: Filter by parent (None for root categories)
            is_system: Filter by system status
            include_subcategories: Include all subcategories in results
        """
        query = self.db.query(Category).filter(Category.user_id == user_id)

        if category_type:
            query = query.filter(Category.category_type == category_type)
        
        if parent_id is not None:
            query = query.filter(Category.parent_id == parent_id)
        elif not include_subcategories:
            # Only root categories (no parent)
            query = query.filter(Category.parent_id.is_(None))
        
        if is_system is not None:
            query = query.filter(Category.is_system == is_system)

        query = query.order_by(Category.name)

        return query.all()

    def get_category_hierarchy(self, category_id: int, user_id: int) -> List[Category]:
        """Get category and all its descendants"""
        category = self.get_category(category_id, user_id)
        if not category:
            raise NotFoundError(f"Category with ID {category_id} not found")
        
        result = [category]
        self._add_descendants(category, result)
        return result

    def _add_descendants(self, category: Category, result: List[Category]):
        """Recursively add all descendants to result list"""
        for child in category.subcategories:
            result.append(child)
            self._add_descendants(child, result)

    def update_category(
        self,
        category_id: int,
        user_id: int,
        name: Optional[str] = None,
        category_type: Optional[str] = None,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
        matching_pattern: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
    ) -> Category:
        """Update category"""
        category = self.get_category(category_id, user_id)
        if not category:
            raise NotFoundError(f"Category with ID {category_id} not found")
        
        # Cannot update system categories
        if category.is_system:
            raise ValidationError("System categories cannot be modified")

        # Validate updates
        if name is not None:
            self._validate_name(name)
            # Check for duplicate if name changed
            if name != category.name:
                existing = self._get_category_by_name(user_id, name)
                if existing:
                    raise AlreadyExistsError(f"Category with name '{name}' already exists")
            category.name = name.strip()
        
        if category_type is not None:
            self._validate_category_type(category_type)
            # If changing type, ensure no parent or update parent
            if category.parent_id and category_type != category.parent.category_type:
                raise ValidationError("Cannot change type when category has a parent with different type")
            category.category_type = category_type
        
        if parent_id is not None:
            # Validate parent exists
            parent = self.get_category(parent_id, user_id)
            if not parent:
                raise NotFoundError(f"Parent category with ID {parent_id} not found")
            # Prevent circular references
            if parent_id == category_id:
                raise ValidationError("Category cannot be its own parent")
            # Check if parent_id would create a cycle
            if self._would_create_cycle(category_id, parent_id):
                raise ValidationError("Setting this parent would create a circular reference")
            # Ensure same type
            if parent.category_type != category.category_type:
                raise ValidationError("Parent and child categories must have the same type")
            category.parent_id = parent_id
        
        if description is not None:
            category.description = description
        if matching_pattern is not None:
            category.matching_pattern = matching_pattern
        if color is not None:
            category.color = color
        if icon is not None:
            category.icon = icon

        self.db.commit()
        self.db.refresh(category)

        return category

    def delete_category(self, category_id: int, user_id: int) -> bool:
        """Delete category"""
        category = self.get_category(category_id, user_id)
        if not category:
            raise NotFoundError(f"Category with ID {category_id} not found")
        
        # Cannot delete system categories
        if category.is_system:
            raise ValidationError("System categories cannot be deleted")
        
        # Check if has subcategories
        if category.subcategories:
            raise ValidationError("Cannot delete category with subcategories. Delete children first.")

        self.db.delete(category)
        self.db.commit()

        return True

    # Private validation methods

    def _validate_name(self, name: str):
        """Validate category name"""
        if not name or not name.strip():
            raise ValidationError("Name cannot be empty")
        if len(name) > 100:
            raise ValidationError("Name cannot exceed 100 characters")

    def _validate_category_type(self, category_type: str):
        """Validate category type"""
        if category_type not in self.VALID_CATEGORY_TYPES:
            raise ValidationError(
                f"Invalid category_type. Must be one of: {', '.join(self.VALID_CATEGORY_TYPES)}"
            )

    def _get_category_by_name(self, user_id: int, name: str) -> Optional[Category]:
        """Get category by name for user"""
        return (
            self.db.query(Category)
            .filter(
                Category.user_id == user_id,
                Category.name == name.strip(),
            )
            .first()
        )

    def _would_create_cycle(self, category_id: int, new_parent_id: int) -> bool:
        """Check if setting new_parent_id would create a circular reference"""
        # Walk up the tree from new_parent to see if we hit category_id
        current_id = new_parent_id
        visited = set()
        
        while current_id:
            if current_id == category_id:
                return True  # Cycle detected
            if current_id in visited:
                return True  # Already visited, circular reference exists
            visited.add(current_id)
            
            # Get parent of current
            category = self.db.query(Category).filter(Category.id == current_id).first()
            if not category:
                break
            current_id = category.parent_id
        
        return False
