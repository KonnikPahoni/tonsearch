import logging
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand

from tonnftscan.models import Collection
from tonnftscan.settings import BASE_DIR


class Command(BaseCommand):
    help = "Generate sitemap."

    def handle(self, *args, **options):
        # List of URLs
        urls = [
            "https://tonsearch.org",
            "https://tonsearch.org/collections",
            "https://tonsearch.org/wallets",
            "https://tonsearch.org/nfts",
        ]

        collections_filterset = Collection.objects.filter(nfts_count__gt=0)
        logging.info(f"Collections count: {collections_filterset.count()}")

        for collection in collections_filterset:
            urls.append(collection.get_url())

        # define urlset with necessary namespace
        urlset = ET.Element("urlset", {"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"})

        # iterate over urls
        for url in urls:
            # define url element
            url_element = ET.SubElement(urlset, "url")

            # add loc subelement
            ET.SubElement(url_element, "loc").text = url

        # wrap it in an ElementTree instance, and save as XML
        tree = ET.ElementTree(urlset)

        # write the tree to a file
        tree.write(BASE_DIR / "tonnftscan/static/sitemap.xml", encoding="utf-8", xml_declaration=True)

        self.stdout.write(f"Done generating sitemap: {len(urls)}")
