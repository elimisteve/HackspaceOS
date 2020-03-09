from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Update the database"

    def handle(self, *args, **options):
        from _database.models import Event, Consensus, Person, Wish, Photo, Project
        from _setup.config import Config
        from _setup.secrets import Secret
        from _setup.asci_art import show_message
        import time
        import requests

        show_message('I will now start to update your database, based on your secrets.json and config.json. Depending on your settings, amount of events & photos & Discourse entries from your hackerspace this can take everything from seconds to hours (?). But you can already test your website - by opening a new terminal window and run "python manage.py runserver 0.0.0.0:8000" - and open 0.0.0.0:8000 in your web browser.')
        time.sleep(5)

        # import data from Discourse
        Person.objects.import_from_discourse()
        Consensus.objects.import_from_discourse()
        Project.objects.import_from_discourse()
        # TODO Adding Wishlist
        # Wish.objects.import_from_discourse()

        # import events from Meetup
        Event.objects.import_from_meetup()
        extra_groups = Config('EVENTS.EXTRA_MEETUP_GROUPS').value
        if extra_groups:
            show_message(
                'Import events from additional Meetup groups ...')
            time.sleep(2)
            for group in extra_groups:
                Event.objects.import_from_meetup(group)

        # import photos
        show_message('Start importing your existing photos from the web ...')
        time.sleep(2)

        Photo.objects.import_from_google_photos()
        Photo.objects.import_from_twitter()
        Photo.objects.import_from_wiki()
        Photo.objects.import_from_instagram()
        Photo.objects.import_from_flickr()

        show_message(
            '✅ Done! I updated the database')
        time.sleep(2)
