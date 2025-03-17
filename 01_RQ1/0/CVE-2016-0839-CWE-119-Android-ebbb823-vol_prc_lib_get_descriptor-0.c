static int vol_prc_lib_get_descriptor(const effect_uuid_t *uuid,
 effect_descriptor_t *descriptor)
{
 int i = 0;
    ALOGV("%s Called ", __func__);
 if (lib_init() != 0) {
 return init_status;
 }

 if (descriptor == NULL || uuid == NULL) {
        ALOGE("%s: %s is NULL", __func__, (descriptor == NULL) ? "descriptor" : "uuid");
 return -EINVAL;
 }

 for (i = 0; descriptors[i] != NULL; i++) {
 if (memcmp(uuid, &descriptors[i]->uuid, sizeof(effect_uuid_t)) == 0) {
 *descriptor = *descriptors[i];
 return 0;
 }
 }

    ALOGE("%s: couldnt found uuid passed, oops", __func__);
 return -EINVAL;
}
