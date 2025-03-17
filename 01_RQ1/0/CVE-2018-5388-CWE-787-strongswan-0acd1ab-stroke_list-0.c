static void stroke_list(private_stroke_socket_t *this, stroke_msg_t *msg,
						FILE *out)
{
	if (msg->list.flags & LIST_CAINFOS)
	{
		this->ca->list(this->ca, msg, out);
	}
	this->list->list(this->list, msg, out);
}
