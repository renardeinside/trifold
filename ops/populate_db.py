"""
Script to populate the desserts table with sample data.
"""

from trifold.app.config import rt
from trifold.app.database import create_db_and_tables
from trifold.app.models import Dessert
from sqlmodel import select
import sys


def populate_desserts():
    """Populate the desserts table with sample data."""

    # Create tables if they don't exist
    create_db_and_tables()

    # Define the 6 desserts with varied data
    desserts_data = [
        {
            "name": "Apple Strudel",
            "price": 8.50,
            "description": "Traditional Austrian pastry with tender apples, cinnamon, and flaky phyllo dough, served warm with vanilla ice cream",
            "left_in_stock": 12,
        },
        {
            "name": "New York Cheesecake",
            "price": 9.95,
            "description": "Classic rich and creamy cheesecake with graham cracker crust, topped with fresh berry compote",
            "left_in_stock": 8,
        },
        {
            "name": "Chocolate Lava Cake",
            "price": 11.25,
            "description": "Decadent dark chocolate cake with a molten chocolate center, served with premium vanilla gelato",
            "left_in_stock": 15,
        },
        {
            "name": "Crème Brûlée",
            "price": 7.75,
            "description": "Silky vanilla custard topped with caramelized sugar and garnished with fresh mint and berries",
            "left_in_stock": 6,
        },
        {
            "name": "Tiramisu",
            "price": 8.95,
            "description": "Italian coffee-flavored dessert with layers of mascarpone, ladyfingers, and dusted with cocoa powder",
            "left_in_stock": 10,
        },
        {
            "name": "Lemon Tart",
            "price": 6.50,
            "description": "Buttery pastry shell filled with tangy lemon curd and topped with toasted meringue peaks",
            "left_in_stock": 18,
        },
    ]

    with rt.session as session:
        # Check if desserts already exist to avoid duplicates
        existing_desserts = session.exec(select(Dessert)).all()
        existing_names = {dessert.name for dessert in existing_desserts}

        rt.logger.info(f"Found {len(existing_desserts)} existing desserts in database")

        # Add only new desserts
        added_count = 0
        for dessert_data in desserts_data:
            if dessert_data["name"] not in existing_names:
                dessert = Dessert(**dessert_data)
                session.add(dessert)
                added_count += 1
                rt.logger.info(
                    f"Added dessert: {dessert_data['name']} - ${dessert_data['price']:.2f}"
                )
            else:
                rt.logger.info(
                    f"Dessert '{dessert_data['name']}' already exists, skipping"
                )

        # Commit all changes
        session.commit()
        rt.logger.info(f"Successfully added {added_count} new desserts to the database")

        # Display final count
        total_desserts = session.exec(select(Dessert)).all()
        rt.logger.info(f"Total desserts in database: {len(total_desserts)}")


if __name__ == "__main__":
    try:
        rt.logger.info("Starting dessert database population...")
        populate_desserts()
        rt.logger.info("Dessert database population completed successfully!")
    except Exception as e:
        rt.logger.error(f"Error populating desserts database: {e}")
        sys.exit(1)
