static void edge_break(struct tty_struct *tty, int break_state)
{
	struct usb_serial_port *port = tty->driver_data;
	struct edgeport_port *edge_port = usb_get_serial_port_data(port);
	int status;
	int bv = 0;	/* Off */

	if (break_state == -1)
		bv = 1;	/* On */
	status = ti_do_config(edge_port, UMPC_SET_CLR_BREAK, bv);
	if (status)
		dev_dbg(&port->dev, "%s - error %d sending break set/clear command.\n",
			__func__, status);
}
