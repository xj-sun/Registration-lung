from __future__ import print_function
from itkGUI import GUI
import SimpleITK as sitk
from math import pi
import sys
import os

class Registration():


    def command_iteration(self,method):

        self.method = method
        if (self.method.GetOptimizerIteration() == 0):
            print("Scales: ", self.method.GetOptimizerScales())
        print("{0:3} = {1:10.5f} : {2}".format(self.method.GetOptimizerIteration(),
                                               self.method.GetMetricValue(),
                                               self.method.GetOptimizerPosition()))


    def command_bs_iteration(self,method) :
        self.method = method

        print("{0:3} = {1:10.5f}".format(self.method.GetOptimizerIteration(),
                                     self.method.GetMetricValue()))

    def command_ds_iteration(self,method):

        self.method = method

        if (self.method.GetOptimizerIteration() == 0):
            print("\tLevel: {0}".format(self.method.GetCurrentLevel()))
            print("\tScales: {0}".format(self.method.GetOptimizerScales()))
        print("#{0}".format(self.method.GetOptimizerIteration()))
        print("\tMetric Value: {0:10.5f}".format(self.method.GetMetricValue()))
        print("\tLearningRate: {0:10.5f}".format(self.method.GetOptimizerLearningRate()))
        if (self.method.GetOptimizerConvergenceValue() != sys.float_info.max):
            print("\tConvergence Value: {0:.5e}".format(self.method.GetOptimizerConvergenceValue()))

    def command_multibs_iteration(self,method) :
    # The sitkMultiResolutionIterationEvent occurs before the
    # resolution of the transform. This event is used here to print
    # the status of the optimizer from the previous registration level.
        self.R = method
        if self.R.GetCurrentLevel() > 0:
            self.runPrint(None, self.R)

        print("--------- Resolution Changing ---------")

    def runPrint(self, outTx, method):

        self.outTx = outTx
        self.R = method
        print("-------")
        if self.outTx:
            print(self.outTx)
        print("Optimizer stop condition: {0}".format(self.R.GetOptimizerStopConditionDescription()))
        print(" Iteration: {0}".format(self.R.GetOptimizerIteration()))
        print(" Metric value: {0}".format(self.R.GetMetricValue()))

    def reSample(self, fixed, outTx, moving, pixvalue):

        self.pixvale = pixvalue
        self.fixed  = fixed
        self.outTx = outTx
        self.moving = moving
        resampler = sitk.ResampleImageFilter()
        resampler.SetReferenceImage(self.fixed)
        resampler.SetInterpolator(sitk.sitkLinear)
        resampler.SetDefaultPixelValue(self.pixvale)
        resampler.SetTransform(self.outTx)

        out = resampler.Execute(self.moving)
        simg1 = sitk.Cast(sitk.RescaleIntensity(self.fixed), sitk.sitkUInt8)
        simg2 = sitk.Cast(sitk.RescaleIntensity(out), sitk.sitkUInt8)
        cimg = sitk.Compose(simg1, simg2, simg1 // 2. + simg2 // 2.)

        return [simg2, cimg]

    def registrationAffine(self): #rigid method

        num = GUI().initImage()[0]
        fixFiles = GUI().initImage()[1]
        moveFiles = GUI().initImage()[2]
        fixDir = GUI().initImage()[3]
        moveDir = GUI().initImage()[4]
        fixed = sitk.ReadImage(os.path.join(fixDir, fixFiles[0]), sitk.sitkFloat32)

        for index in range(num):

            #fixed = sitk.ReadImage(os.path.join(fixDir, fixFiles[index]), sitk.sitkFloat32)
            moving = sitk.ReadImage(os.path.join(moveDir, moveFiles[index]), sitk.sitkFloat32)

            initialTx = sitk.CenteredTransformInitializer(fixed, moving, sitk.AffineTransform(fixed.GetDimension()))
            R = sitk.ImageRegistrationMethod()
            R.SetShrinkFactorsPerLevel([3, 2, 1])
            R.SetSmoothingSigmasPerLevel([2, 1, 1])
            R.SetMetricAsJointHistogramMutualInformation(20)
            R.MetricUseFixedImageGradientFilterOff()
            R.SetOptimizerAsGradientDescent(learningRate=1.0,
                                            numberOfIterations=300,
                                            convergenceMinimumValue=1e-6,
                                            estimateLearningRate=R.EachIteration)
            R.SetOptimizerScalesFromPhysicalShift()
            R.SetInitialTransform(initialTx, inPlace=True)
            R.SetInterpolator(sitk.sitkLinear)
            R.AddCommand(sitk.sitkIterationEvent, lambda: self.command_ds_iteration(R))
            # R.AddCommand(sitk.sitkMultiResolutionIterationEvent, lambda: command_multiresolution_iteration(R))

            outTx = R.Execute(fixed, moving)

            self.runPrint(outTx, R)

            resImage = self.reSample(fixed, outTx, moving, 100)
            resName = moveFiles[index].split(".", 1)[0] + '_Affine'
            GUI().writeImage(resImage[0], resImage[1], resName)


    def registrationBSpline(self): #rigid method

        num = GUI().initImage()[0]
        fixFiles = GUI().initImage()[1]
        moveFiles = GUI().initImage()[2]
        fixDir = GUI().initImage()[3]
        moveDir = GUI().initImage()[4]
        fixed = sitk.ReadImage(os.path.join(fixDir, fixFiles[0]), sitk.sitkFloat32)

        for index in range(num):

            #fixed = sitk.ReadImage(os.path.join(fixDir, fixFiles[index]), sitk.sitkFloat32)
            moving = sitk.ReadImage(os.path.join(moveDir, moveFiles[index]), sitk.sitkFloat32)

            transformDomainMeshSize = [2] * fixed.GetDimension()
            tx = sitk.BSplineTransformInitializer(fixed,
                                                  transformDomainMeshSize)

            print("Initial Number of Parameters: {0}".format(tx.GetNumberOfParameters()))

            R = sitk.ImageRegistrationMethod()
            R.SetMetricAsJointHistogramMutualInformation()
            R.SetOptimizerAsGradientDescentLineSearch(3.0,
                                                      200,
                                                      convergenceMinimumValue=1e-5,
                                                      convergenceWindowSize=5)
            R.SetInterpolator(sitk.sitkLinear)
            R.SetInitialTransformAsBSpline(tx,
                                           inPlace=True,
                                           scaleFactors=[1, 2, 5])
            R.SetShrinkFactorsPerLevel([4, 2, 1])
            R.SetSmoothingSigmasPerLevel([4, 2, 1])
            R.AddCommand(sitk.sitkIterationEvent, lambda: self.command_bs_iteration(R))
            R.AddCommand(sitk.sitkMultiResolutionIterationEvent, lambda: self.command_multibs_iteration(R))

            outTx = R.Execute(fixed, moving)
            self.runPrint(outTx, R)

            resImage = self.reSample(fixed, outTx, moving, 100)
            resName = moveFiles[index].split(".", 1)[0] + '_BSpline'
            GUI().writeImage(resImage[0], resImage[1], resName)