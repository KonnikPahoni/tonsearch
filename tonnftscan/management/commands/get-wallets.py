import base64
import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from tonnftscan.constants import AddressType
from tonnftscan.models import Collection, NFT, Address
from tonnftscan.utils import convert_hex_address_to_user_friendly


class Command(BaseCommand):
    help = f"Finds wallet for an airdrop"

    addresses_needed = 300
    addresses_found = 0
    key_words = [
        "cannabis",
        "spliff",
        "weed",
        "MDMA",
        "LSD",
        "cocaine",
        "heroin",
        "amphetamine",
        "methamphetamine",
        "mephedrone",
        "marijuana",
        "hashish",
        "ketamine",
        "ecstasy",
        "harm reduction",
        "psychedelic",
        "drugs",
        "tripping",
        "overdose",
        "legalize",
        "легалайз",
        "марихуана",
        "травка",
        "кокаин",
        "героин",
        "экстази",
        "метамфетамин",
        "мефедрон",
        "кетамин",
        "психоделик",
        "ЛСД",
        "МДМА",
        "спайс",
        "Smoking",
        "vodka",
        "Кратом",
        "Крокодил",
        "Belarus",
        "беларус",
        "лукашенко",
        "Snoop Dogg",
        "снуп догг",
        "водка",
        "курить",
        "курение",
        "пивасик",
        "тихановская",
        "белорус",
        "активист",
        "протест",
        "протесты",
        "activist",
        "protest",
        "protests",
        "opioid",
        "rehab",
        "recovery",
        "addiction",
        "Stimulant",
        "Lexapro",
        "antidepressant",
        "Антидепрессант",
        "Каліноўск",
        "hydra",
        "наркотик",
        "наркоман",
        "psylocibin",
        "псилоцибин",
        "гриб",
        "Peyote",
        "Ayahuasca",
        "Аяхуаска",
        "Мухомор",
        "галлюциноген",
        "Chemical",
        "Legalization",
        "Decriminalization",
        "Decriminalisation",
        "methadone",
        "декреминализация",
        "тюрьма",
        "уголовный кодекс",
        "психотроп",
        "Mind-altering",
        "Vaporizing",
        "vaping",
        "Sobriety",
        "Synthetic cannabinoids",
        "cannabinoid",
        "cbd",
        "thc",
        "cannabidiol",
        "КБД",
        "ТГК",
        "Гандж",
        "medicine",
        "лекарство",
        "лечение",
        "therapy",
        "терапия",
        "Минск",
        "Minsk",
        "Гомель",
        "Гродна",
        "БЧБ",
        "Пагоня",
        "змагар",
        "Substance",
        "detox",
        "нарколог",
        "травка",
        "prison",
        "boss",
        "сигарета",
        "indica",
        "sativa",
        "конопля",
        "индика",
        "сатива",
    ]

    def handle(self, *args, **options):
        last_activity_limit = timezone.now() - timedelta(days=360)

        nft_filterset = NFT.objects.filter(
            owner__last_activity__gt=last_activity_limit, owner__address_type=AddressType.WALLET, owner__is_scam=False
        )

        key_word_index = 0

        addresses_set = set()
        total_found = 0

        while self.addresses_found < self.addresses_needed:
            # Looking for NFTs with key words in name
            nft_filterset_filtered = nft_filterset.filter(name__icontains=self.key_words[key_word_index])
            nft_owner_addresses = list(nft_filterset_filtered.values_list("owner__address", flat=True).distinct())
            new_addresses_found = len(set(nft_owner_addresses) - set(addresses_set))
            if new_addresses_found > 0:
                total_found += new_addresses_found
                logging.info(
                    f"{new_addresses_found} NFT owners found containing {self.key_words[key_word_index]} in name"
                )
            self.addresses_found += new_addresses_found
            addresses_set.update(nft_owner_addresses)

            # Looking for NFTs with key words in description
            nft_filterset_filtered = nft_filterset.filter(description__icontains=self.key_words[key_word_index])
            nft_owner_addresses = list(nft_filterset_filtered.values_list("owner__address", flat=True).distinct())
            new_addresses_found = len(set(nft_owner_addresses) - set(addresses_set))
            if new_addresses_found > 0:
                total_found += new_addresses_found
                logging.info(
                    f"{new_addresses_found} NFT owners found containing {self.key_words[key_word_index]} in description"
                )
            self.addresses_found += new_addresses_found
            addresses_set.update(nft_owner_addresses)

            # Looking for Collections with key words in name
            collections_filterset = Collection.objects.filter(name__icontains=self.key_words[key_word_index])
            collection_owner_addresses = list(collections_filterset.values_list("owner__address", flat=True).distinct())
            new_addresses_found = len(set(collection_owner_addresses) - set(addresses_set))
            if new_addresses_found > 0:
                total_found += new_addresses_found
                logging.info(
                    f"{new_addresses_found} collection owners found containing {self.key_words[key_word_index]} in name"
                )
            self.addresses_found += new_addresses_found
            addresses_set.update(collection_owner_addresses)

            # Looking for Collections with key words in description
            collections_filterset = Collection.objects.filter(description__icontains=self.key_words[key_word_index])
            collection_owner_addresses = list(collections_filterset.values_list("owner__address", flat=True).distinct())
            new_addresses_found = len(set(collection_owner_addresses) - set(addresses_set))
            if new_addresses_found > 0:
                total_found += new_addresses_found
                logging.info(
                    f"{new_addresses_found} collection owners found containing {self.key_words[key_word_index]} in name"
                )
            self.addresses_found += new_addresses_found
            addresses_set.update(collection_owner_addresses)

            key_word_index += 1
            if key_word_index >= len(self.key_words):
                logging.error("No more key words")
                break

        # Remove wallets who do not have enough NFTs

        final_addresses = []

        # for address in addresses_set:
        #     address_object = Address.objects.get(address=address)
        #     nfts_count = NFT.objects.filter(owner=address_object).count()

        logging.info(f"Found {len(addresses_set)} addresses")

        last_activity_limit = timezone.now() - timedelta(days=5)
        additional_addresses = Address.objects.filter(
            last_activity__gt=last_activity_limit, address_type=AddressType.WALLET, is_scam=False
        ).order_by("-last_activity")

        for additional_address in additional_addresses:
            if additional_address.address not in addresses_set:
                nfts_count = NFT.objects.filter(owner=additional_address).count()
                if nfts_count > 3 and nfts_count < 20:
                    logging.info(
                        f"Found additional address {additional_address.address} with {nfts_count} NFTs, last activity {additional_address.last_activity}"
                    )
                    addresses_set.add(additional_address.address)

            if len(addresses_set) == self.addresses_needed:
                break

        with open("var/wallets.txt", "w") as f:
            for address in addresses_set:
                f.write(f"{convert_hex_address_to_user_friendly(address)}\n")
