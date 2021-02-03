# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""Django management command to synchronize statement forwarders."""
from django.core.management import BaseCommand
from django.conf import settings

from assistants.models import Assistant
import assistants.learning_locker as ll
from lib.ll_get_parsers import parse_batch_parse_statement_forwarder_id_url
import assistants.sync_agent as sync_agent


class Command(BaseCommand):
    """Synchronize the Mofa assistants with the statement forwarders in Learning Locker."""

    help = "Synchronize the Mofa assistants with the statement forwarders in Learning Locker."

    def handle(self, *args, **options):
        """Run command."""
        print("This command will synchronize Learning Locker with Mofa. Orphaned statement forwarders in Learning "
              "Locker will be deleted.")

        yes = {'yes', 'y'}
        no = {'no', 'n', ''}

        choice = input("Do you want to proceed? [y/N]:").lower()
        if choice in yes:
            self.check_statement_forwarder_sync()
            self.check_sync_agent_forwarders()
        if choice in no:
            return

    def check_statement_forwarder_sync(self):
        """Check if the statement forwarders are up to date with Mofa."""
        assistants_classes = [list(model.objects.all()) for model in Assistant.__subclasses__()]
        assistants = [x for llist in assistants_classes for x in llist]

        forwarders = parse_batch_parse_statement_forwarder_id_url(ll.get_all_statement_forwarders())
        assistants_dict = {}

        for assistant in assistants:
            assistants_dict[assistant.forwarder_id] = assistant

        status = True
        for forwarder in forwarders:
            if forwarder['id'] in assistants_dict.keys():
                del (assistants_dict[forwarder['id']])
            elif forwarder['url'] not in settings.SYNC_AGENT_URLS.values():
                status = False
                self.stdout.write(f'Learning Locker not in sync... '
                                  f'Removing orphan statement forwarder with id: {forwarder["id"]}')
                ll.delete_statement_forwarder(forwarder['id'])

        if len(assistants_dict) == 0 and status:
            self.stdout.write("Assistant forwarders are up to date.")
            return

        for _, assistant in assistants_dict.items():
            self.stdout.write(f'Learning Locker not in sync... Creating statement forwarder for: {assistant.name}')
            assistant.save()

    def check_sync_agent_forwarders(self):
        """Check if the statement forwarders for the sync agents are up to date."""
        sync_agent.build_sync_agents()
        self.stdout.write('Sync_agent forwarders are up to date.')
