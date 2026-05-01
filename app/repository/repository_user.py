from sqlalchemy import select

from app.db.database import SessionDep

from app.models.model_users import UserModel, RolePermissionModel, PermissionModel, ResourcesEnum, ActionEnum


class UserRepository:
    @classmethod
    async def get_permission(cls, user: UserModel, resource: ResourcesEnum, action: ActionEnum, session: SessionDep) -> tuple[str] | None:
        role_permissions_query = await session.execute(
            select(RolePermissionModel.permission_id)
            .where(RolePermissionModel.role_id == user.role_id)
        )
        permission_ids = [row[0] for row in role_permissions_query.all()]

        permission_query = await session.execute(
            select(PermissionModel)
            .where(
                PermissionModel.permission_id.in_(permission_ids),
                PermissionModel.resources == resource,
                PermissionModel.action == action
            )
        )
        return permission_query.first()
    
    @classmethod
    async def has_permission(cls, user: UserModel, session: SessionDep, resource: ResourcesEnum, action: ActionEnum) -> bool:
        if not user or not user.is_active:
            return False
        
        permission = await cls.get_permission(user=user, resource=resource, action=action, session=session)

        return permission is not None
    
    @classmethod
    async def set_active(cls, user_id, is_active: bool, session: SessionDep) -> bool:
        result = await session.execute(select(UserModel).where(UserModel.user_id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.is_active = is_active
            session.add(user)
            await session.commit()
            return True
        return False