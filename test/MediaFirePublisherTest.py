import publisher.MediaFirePublisher as mfp

publisher = mfp.MediaFirePublisher("username", "password")
publisher.upload("IMG_20150801_180120.jpg", "/Tmp/test.jpg")
