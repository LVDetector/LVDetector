rdpdr_send_client_capability_response(void)
{
	/* DR_CORE_CAPABILITY_RSP */
	STREAM s;
	s = channel_init(rdpdr_channel, 0x50);

	out_uint16_le(s, RDPDR_CTYP_CORE);	/* Header */
	out_uint16_le(s, PAKID_CORE_CLIENT_CAPABILITY);	/* Header */
	out_uint16_le(s, 5);	/* numCapabilities */
	out_uint16_le(s, 0);	/* Padding */

	out_uint16_le(s, CAP_GENERAL_TYPE);	/* CapabilityType */
	out_uint16_le(s, 0x28);	/* CapabilityLength */
	out_uint32_le(s, GENERAL_CAPABILITY_VERSION_01);	/* Version */
	out_uint32_le(s, 0);	/* osType */
	out_uint32_le(s, 0);	/* osVersion */
	out_uint16_le(s, 1);	/* protocolMajorVersion */
	out_uint16_le(s, 5);	/* protocolMinorVersion */
	out_uint32_le(s, ALL_RDPDR_IRP_MJ);	/* ioCode1 */
	out_uint32_le(s, 0);	/* ioCode2 */
	out_uint32_le(s, RDPDR_DEVICE_REMOVE_PDUS | RDPDR_CLIENT_DISPLAY_NAME_PDU);	/* extendedPDU */
	out_uint32_le(s, 0);	/* extraFlags1 */
	out_uint32_le(s, 0);	/* extraFlags2 */

	out_uint16_le(s, CAP_PRINTER_TYPE);	/* CapabilityType */
	out_uint16_le(s, 8);	/* CapabilityLength */
	out_uint32_le(s, PRINT_CAPABILITY_VERSION_01);	/* Version */

	out_uint16_le(s, CAP_PORT_TYPE);	/* CapabilityType */
	out_uint16_le(s, 8);	/* CapabilityLength */
	out_uint32_le(s, PORT_CAPABILITY_VERSION_01);	/* Version */

	out_uint16_le(s, CAP_DRIVE_TYPE);	/* CapabilityType */
	out_uint16_le(s, 8);	/* CapabilityLength */
	out_uint32_le(s, DRIVE_CAPABILITY_VERSION_02);	/* Version */

	out_uint16_le(s, CAP_SMARTCARD_TYPE);	/* CapabilityType */
	out_uint16_le(s, 8);	/* CapabilityLength */
	out_uint32_le(s, SMARTCARD_CAPABILITY_VERSION_01);	/* Version */

	s_mark_end(s);
	channel_send(s, rdpdr_channel);
}
