import loadimg

class ImgLoaderURL(loadimg.ImgLoader):
    url : str = None
    def prepare(self):
        self.imageb = self.loadImgCURL( self.url )
