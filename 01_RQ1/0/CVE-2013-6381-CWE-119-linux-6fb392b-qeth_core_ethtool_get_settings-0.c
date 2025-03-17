int qeth_core_ethtool_get_settings(struct net_device *netdev,
					struct ethtool_cmd *ecmd)
{
	struct qeth_card *card = netdev->ml_priv;
	enum qeth_link_types link_type;

	if ((card->info.type == QETH_CARD_TYPE_IQD) || (card->info.guestlan))
		link_type = QETH_LINK_TYPE_10GBIT_ETH;
	else
		link_type = card->info.link_type;

	ecmd->transceiver = XCVR_INTERNAL;
	ecmd->supported = SUPPORTED_Autoneg;
	ecmd->advertising = ADVERTISED_Autoneg;
	ecmd->duplex = DUPLEX_FULL;
	ecmd->autoneg = AUTONEG_ENABLE;

	switch (link_type) {
	case QETH_LINK_TYPE_FAST_ETH:
	case QETH_LINK_TYPE_LANE_ETH100:
		ecmd->supported |= SUPPORTED_10baseT_Half |
					SUPPORTED_10baseT_Full |
					SUPPORTED_100baseT_Half |
					SUPPORTED_100baseT_Full |
					SUPPORTED_TP;
		ecmd->advertising |= ADVERTISED_10baseT_Half |
					ADVERTISED_10baseT_Full |
					ADVERTISED_100baseT_Half |
					ADVERTISED_100baseT_Full |
					ADVERTISED_TP;
		ecmd->speed = SPEED_100;
		ecmd->port = PORT_TP;
		break;

	case QETH_LINK_TYPE_GBIT_ETH:
	case QETH_LINK_TYPE_LANE_ETH1000:
		ecmd->supported |= SUPPORTED_10baseT_Half |
					SUPPORTED_10baseT_Full |
					SUPPORTED_100baseT_Half |
					SUPPORTED_100baseT_Full |
					SUPPORTED_1000baseT_Half |
					SUPPORTED_1000baseT_Full |
					SUPPORTED_FIBRE;
		ecmd->advertising |= ADVERTISED_10baseT_Half |
					ADVERTISED_10baseT_Full |
					ADVERTISED_100baseT_Half |
					ADVERTISED_100baseT_Full |
					ADVERTISED_1000baseT_Half |
					ADVERTISED_1000baseT_Full |
					ADVERTISED_FIBRE;
		ecmd->speed = SPEED_1000;
		ecmd->port = PORT_FIBRE;
		break;

	case QETH_LINK_TYPE_10GBIT_ETH:
		ecmd->supported |= SUPPORTED_10baseT_Half |
					SUPPORTED_10baseT_Full |
					SUPPORTED_100baseT_Half |
					SUPPORTED_100baseT_Full |
					SUPPORTED_1000baseT_Half |
					SUPPORTED_1000baseT_Full |
					SUPPORTED_10000baseT_Full |
					SUPPORTED_FIBRE;
		ecmd->advertising |= ADVERTISED_10baseT_Half |
					ADVERTISED_10baseT_Full |
					ADVERTISED_100baseT_Half |
					ADVERTISED_100baseT_Full |
					ADVERTISED_1000baseT_Half |
					ADVERTISED_1000baseT_Full |
					ADVERTISED_10000baseT_Full |
					ADVERTISED_FIBRE;
		ecmd->speed = SPEED_10000;
		ecmd->port = PORT_FIBRE;
		break;

	default:
		ecmd->supported |= SUPPORTED_10baseT_Half |
					SUPPORTED_10baseT_Full |
					SUPPORTED_TP;
		ecmd->advertising |= ADVERTISED_10baseT_Half |
					ADVERTISED_10baseT_Full |
					ADVERTISED_TP;
		ecmd->speed = SPEED_10;
		ecmd->port = PORT_TP;
	}

	return 0;
}
