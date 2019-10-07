
import matplotlib.pyplot as plt
import SimpleITK as sitk
import nibabel as nib
import time
import os
import sys

class GUI():


    # create directory for results and return the number of images which needed to registration
    #@classmethod
    def initImage(self):

        self.Dir = sys.path[0]
        self.subDir = os.listdir(self.Dir)
        for _ in ['resFix', 'resMove', 'resCombine']:
            if _ not in self.subDir:
                os.mkdir(os.path.join(self.Dir, _))
        fixDir = os.path.join(self.Dir, 'fixDir')
        moveDir = os.path.join(self.Dir, 'moveDir')
        fixFiles = list (filter(lambda x: x.endswith('.gz') or x.endswith('.nii'),os.listdir(fixDir)))
        moveFiles = list (filter(lambda x: x.endswith('.gz') or x.endswith('.nii'),os.listdir(moveDir)))

        return [min(len(fixFiles), len(moveFiles)), fixFiles, moveFiles, fixDir, moveDir]



    # with the results to the resDirectory
    def writeImage( self,resFix, resMove, resCombine, name):

        #fix = sitk.ReadImage(resFix)
        #move = sitk.ReadImage(resMove)
        #combine = sitk.ReadImage(resCombine)
        print('Ready to save resImages')
        self.fix = resFix
        self.move = resMove
        self.combine = resCombine
        self.name = name

        sitk.WriteImage(self.fix, os.path.join(os.path.join(sys.path[0], 'resFix'),
                                                  "{} {}".format(self.name,
                                                                 '_fix_res.nii')))
        sitk.WriteImage(self.move, os.path.join(os.path.join(sys.path[0], 'resMove'),
                                                   "{} {}".format(self.name,
                                                                  '_move_res.nii')))
        sitk.WriteImage(self.combine, os.path.join(os.path.join(sys.path[0], 'resCombine'),
                                                      "{} {}".format(self.name,
                                                                     '_combine_res.nii')))
        print('--------------------------------------')
        print('resImages have been saved successfully')



    def showImage(self, image):

        self.img = image
        image = nib.load(os.path.join('resCombine', self.img))
        self.xDirection = image.dataobj.shape[0]
        self.yDirection = image.dataobj.shape[1]
        self.zDirection = image.dataobj.shape[2]

        fir = plt.figure(1)
        count = 1
        for i in range(0, self.xDirection, 20):
            img_arr = image.dataobj[:, :, i]
            plt.subplot(5, 4, count)
            plt.imshow(img_arr, cmap='gray')
            count += 1

        sen = plt.figure(2)
        count = 1
        for i in range(0, self.yDirection, 20):
            img_arr = image.dataobj[:, i, :]
            plt.subplot(5, 4, count)
            plt.imshow(img_arr, cmap='gray')
            count += 1

        tir = plt.figure(3)
        count = 1
        for i in range(0, self.zDirection, 20):
            img_arr = image.dataobj[i, :, :]
            plt.subplot(5, 4, count)
            plt.imshow(img_arr, cmap='gray')
            count += 1

        plt.show()


