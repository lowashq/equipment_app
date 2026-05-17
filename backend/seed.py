import asyncio
from pathlib import Path

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings
from app.models import Equipment, User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


USERS = [
    {
        "email": "student@student.san.edu.pl",
        "full_name": "Student User",
        "password": "student123",
        "role": "student",
    },
    {
        "email": "staff@san.edu.pl",
        "full_name": "Staff User",
        "password": "staff123",
        "role": "staff",
    },
    {
        "email": "manager@san.edu.pl",
        "full_name": "Equipment Manager",
        "password": "manager123",
        "role": "equipment_manager",
    },
    {
        "email": "admin@san.edu.pl",
        "full_name": "Admin User",
        "password": "admin123",
        "role": "admin",
    },
]


EQUIPMENT = [
    {
        "name": "Dell Latitude 7440",
        "type": "laptop",
        "serial_number": "UER-LAP-001",
        "technical_spec": "Intel Core i7, 16GB RAM, 512GB SSD",
        "location": "Lab A",
        "status": "available",
    },
    {
        "name": "Dell XPS 13",
        "type": "laptop",
        "serial_number": "UER-LAP-002",
        "technical_spec": "Intel Core i7, 16GB RAM, 1TB SSD",
        "location": "Lab B",
        "status": "borrowed",
    },
    {
        "name": "Lenovo ThinkPad X1 Carbon",
        "type": "laptop",
        "serial_number": "UER-LAP-003",
        "technical_spec": "Intel Core i7, 16GB RAM, 512GB SSD",
        "location": "Lab A",
        "status": "available",
    },
    {
        "name": "Lenovo ThinkPad T14",
        "type": "laptop",
        "serial_number": "UER-LAP-004",
        "technical_spec": "AMD Ryzen 7, 16GB RAM, 512GB SSD",
        "location": "Lab B",
        "status": "available",
    },
    {
        "name": "MacBook Pro 14",
        "type": "laptop",
        "serial_number": "UER-LAP-005",
        "technical_spec": "Apple M3 Pro, 18GB RAM, 512GB SSD",
        "location": "Lab A",
        "status": "serviced",
    },
    {
        "name": "MacBook Air M2",
        "type": "laptop",
        "serial_number": "UER-LAP-006",
        "technical_spec": "Apple M2, 8GB RAM, 256GB SSD",
        "location": "Lab B",
        "status": "available",
    },
    {
        "name": "Epson EB-FH52",
        "type": "projector",
        "serial_number": "UER-PRO-001",
        "technical_spec": "Full HD, 4000 lumens",
        "location": "Room 101",
        "status": "available",
    },
    {
        "name": "BenQ MH733",
        "type": "projector",
        "serial_number": "UER-PRO-002",
        "technical_spec": "Full HD, 4000 lumens",
        "location": "Room 101",
        "status": "available",
    },
    {
        "name": "ViewSonic PA503W",
        "type": "projector",
        "serial_number": "UER-PRO-003",
        "technical_spec": "WXGA, 3800 lumens",
        "location": "Room 202",
        "status": "borrowed",
    },
    {
        "name": "Optoma HD146X",
        "type": "projector",
        "serial_number": "UER-PRO-004",
        "technical_spec": "Full HD, 3600 lumens",
        "location": "Room 202",
        "status": "available",
    },
    {
        "name": "Canon EOS 90D",
        "type": "camera",
        "serial_number": "UER-CAM-001",
        "technical_spec": "32.5MP DSLR, 18-135mm lens",
        "location": "Media Room",
        "status": "available",
    },
    {
        "name": "Canon XA60",
        "type": "camera",
        "serial_number": "UER-CAM-002",
        "technical_spec": "4K UHD professional camcorder",
        "location": "Media Room",
        "status": "damaged",
    },
    {
        "name": "Sony Alpha a6400",
        "type": "camera",
        "serial_number": "UER-CAM-003",
        "technical_spec": "24.2MP mirrorless, 16-50mm lens",
        "location": "Media Room",
        "status": "available",
    },
    {
        "name": "Dell PowerEdge R750",
        "type": "server",
        "serial_number": "UER-SRV-001",
        "technical_spec": "2U rack server, Xeon Silver, 128GB RAM",
        "location": "Server Room",
        "status": "available",
    },
    {
        "name": "HPE ProLiant DL380",
        "type": "server",
        "serial_number": "UER-SRV-002",
        "technical_spec": "2U rack server, Xeon Gold, 128GB RAM",
        "location": "Server Room",
        "status": "available",
    },
    {
        "name": "Lenovo ThinkSystem SR650",
        "type": "server",
        "serial_number": "UER-SRV-003",
        "technical_spec": "2U rack server, Xeon Silver, 96GB RAM",
        "location": "Server Room",
        "status": "available",
    },
    {
        "name": "iPad Air",
        "type": "tablet",
        "serial_number": "UER-TAB-001",
        "technical_spec": "10.9-inch display, 64GB Wi-Fi",
        "location": "Library",
        "status": "available",
    },
    {
        "name": "Samsung Galaxy Tab S9",
        "type": "tablet",
        "serial_number": "UER-TAB-002",
        "technical_spec": "11-inch display, 128GB Wi-Fi",
        "location": "Library",
        "status": "available",
    },
    {
        "name": "Rigol DS1054Z",
        "type": "oscilloscope",
        "serial_number": "UER-OSC-001",
        "technical_spec": "50MHz, 4-channel digital oscilloscope",
        "location": "Electronics Lab",
        "status": "available",
    },
    {
        "name": "Tektronix TBS1102B",
        "type": "oscilloscope",
        "serial_number": "UER-OSC-002",
        "technical_spec": "100MHz, 2-channel digital oscilloscope",
        "location": "Electronics Lab",
        "status": "available",
    },
]


def get_database_url() -> str:
    database_url = settings.database_url

    if not Path("/.dockerenv").exists() and "@postgres:" in database_url:
        return database_url.replace("@postgres:", "@localhost:")

    return database_url


async def seed_users(session) -> int:
    created = 0

    for user_data in USERS:
        result = await session.execute(select(User).where(User.email == user_data["email"]))
        user = result.scalar_one_or_none()

        if user is None:
            session.add(
                User(
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    hashed_password=pwd_context.hash(user_data["password"]),
                    role=user_data["role"],
                    is_active=True,
                )
            )
            created += 1
        else:
            user.full_name = user_data["full_name"]
            user.role = user_data["role"]
            user.is_active = True

    return created


async def seed_equipment(session) -> int:
    created = 0

    for item in EQUIPMENT:
        result = await session.execute(
            select(Equipment).where(Equipment.serial_number == item["serial_number"])
        )
        equipment = result.scalar_one_or_none()

        if equipment is None:
            session.add(Equipment(**item))
            created += 1
        else:
            for key, value in item.items():
                setattr(equipment, key, value)

    return created


async def main() -> None:
    engine = create_async_engine(get_database_url(), echo=False)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with session_factory() as session:
        users_created = await seed_users(session)
        equipment_created = await seed_equipment(session)
        await session.commit()

    await engine.dispose()

    print(f"Seed complete: {users_created} users created, {equipment_created} equipment items created.")


if __name__ == "__main__":
    asyncio.run(main())
