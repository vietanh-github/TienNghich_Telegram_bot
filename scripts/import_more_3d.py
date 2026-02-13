
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from database.connection import get_db
from repositories.episode_repository import EpisodeRepository
from database.models import Episode, Link

def import_more_3d():
    """Generate and import 3D episodes 129-200"""
    repo = EpisodeRepository(episode_type="3d")
    count = 0
    updated = 0
    
    print("Starting import for episodes 129-200...")
    
    for number in range(129, 201):
        # Generate URL based on pattern
        url = f"https://tram3d.mom/watch-tien-nghich-thuyet-minh/ep-{number}-sv1.html"
        
        # Check if episode exists
        existing = repo.find_by_episode_number(number)
        
        if existing:
            # Check if link exists
            has_link = False
            if existing.links:
                for link in existing.links:
                    if link.url == url:
                        has_link = True
                        break
            
            if not has_link:
                # Add link
                repo.add_link(number, Link(url=url, source_name="Tram3D"))
                updated += 1
                # print(f"Updated 3D Episode {number}")
        else:
            # Create new
            episode = Episode(
                episode_number=number,
                title=f"Tập {number}",
                links=[Link(url=url, source_name="Tram3D")]
            )
            repo.create(episode)
            count += 1
            print(f"Created 3D Episode {number}")

    print(f"Import finished: {count} created, {updated} updated.")

if __name__ == "__main__":
    db = get_db()
    print("Database connected.")
    
    import_more_3d()
