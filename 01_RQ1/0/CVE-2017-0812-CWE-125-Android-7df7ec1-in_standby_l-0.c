static int in_standby_l(struct stream_in *in)
{
 struct audio_device *adev = in->dev;
 int status = 0;
    lock_input_stream(in);
 if (!in->standby) {
        pthread_mutex_lock(&adev->lock);
        status = do_in_standby_l(in);
        pthread_mutex_unlock(&adev->lock);
 }
    pthread_mutex_unlock(&in->lock);
 return status;
}
