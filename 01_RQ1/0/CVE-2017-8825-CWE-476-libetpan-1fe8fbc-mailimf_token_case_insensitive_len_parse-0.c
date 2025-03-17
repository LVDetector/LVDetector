mailimf_token_case_insensitive_len_parse(const char * message, size_t length,
					 size_t * indx, char * token,
					 size_t token_length)
{
  size_t cur_token;

  cur_token = * indx;

  if (cur_token + token_length - 1 >= length)
    return MAILIMF_ERROR_PARSE;

  if (strncasecmp(message + cur_token, token, token_length) == 0) {
    cur_token += token_length;
    * indx = cur_token;
    return MAILIMF_NO_ERROR;
  }
  else
    return MAILIMF_ERROR_PARSE;
}
