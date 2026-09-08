from .connection import Session
from .models import Champion, Item
from api.dragon import load_champions, load_items

session = Session()

try:
    for champion_id, champion_data in load_champions().items():
        if session.get(Champion, champion_id) is not None:
            continue  # Skip if champion already exists

        champion = Champion(
            id=champion_id,
            name=champion_data["name"],
            normalized_name=champion_data["id"]
        )
        session.add(champion)

    for item_id, item_data in load_items().items():
        if session.get(Item, item_id) is not None:
            continue  # Skip if item already exists

        item = Item(
            id=item_data["id"],
            name=item_data["name"],
            description=item_data["description"],
            plaintext=item_data["plaintext"],
            gold=item_data["gold"],
            tags=item_data["tags"],
            stats=item_data["stats"]
        )
        session.add(item)

    session.commit()
    session.close()
except Exception as e:
    print(f"Error occurred while populating static data: {e}")