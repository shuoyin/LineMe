import networkx as nx

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from LineMe.constants import PROJECT_NAME
from friendnet.models import Link


class Command(BaseCommand):
    help = 'Analysis Links of ' + PROJECT_NAME

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--group', action='append')

    def handle(self, *args, **options):
        for group in options['group']:
            try:
                links = Link.objects.filter(group__group_name=group.upper())
            except Link.DoesNotExist:
                raise CommandError('Group "%s" does not exist' % group)
            self.analyzer(group, links)
        return

    def analyzer(self, group, links):
        G = nx.Graph()

        for link in links:
            G.add_edge(link.source_member.id, link.target_member.id)

        average_degree = 2.0 * G.number_of_edges() / G.number_of_nodes()

        print group, average_degree





