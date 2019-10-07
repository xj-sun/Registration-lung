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

        return [simg1, simg2, cimg]


    def registration_1(self):

        num = GUI().initImage()[0]
        fixFiles = GUI().initImage()[1]
        moveFiles = GUI().initImage()[2]
        fixDir = GUI().initImage()[3]
        moveDir = GUI().initImage()[4]

        for index in range(num):

            fixed = sitk.ReadImage(os.path.join(fixDir,fixFiles[index]), sitk.sitkFloat32)
            moving = sitk.ReadImage(os.path.join(moveDir,moveFiles[index]), sitk.sitkFloat32)

            R = sitk.ImageRegistrationMethod()
            R.SetMetricAsMeanSquares()
            R.SetOptimizerAsRegularStepGradientDescent(4.0, .01, 200)
            R.SetInitialTransform(sitk.TranslationTransform(fixed.GetDimension()))
            R.SetInterpolator(sitk.sitkLinear)
            R.AddCommand(sitk.sitkIterationEvent, lambda: self.command_iteration(R))


            outTx = R.Execute(fixed, moving)

            self.runPrint(outTx, R)

            resImage = self.reSample(fixed, outTx, moving, 100)
            resName = fixFiles[index].split(".", 1)[0] + '_reg1'
            GUI().writeImage(resImage[0], resImage[1], resImage[2], resName)

    def registration_2(self):

        num = GUI().initImage()[0]
        fixFiles = GUI().initImage()[1]
        moveFiles = GUI().initImage()[2]
        fixDir = GUI().initImage()[3]
        moveDir = GUI().initImage()[4]

        for index in range(num):
            fixed = sitk.ReadImage(os.path.join(fixDir, fixFiles[index]), sitk.sitkFloat32)
            fixed = sitk.Normalize(fixed)
            fixed = sitk.DiscreteGaussian(fixed, 2.0)

            moving = sitk.ReadImage(os.path.join(moveDir, moveFiles[index]), sitk.sitkFloat32)
            moving = sitk.Normalize(moving)
            moving = sitk.DiscreteGaussian(moving, 2.0)

            R = sitk.ImageRegistrationMethod()
            R.SetMetricAsJointHistogramMutualInformation()
            R.SetOptimizerAsGradientDescentLineSearch(learningRate=1.0,
                                                      numberOfIterations=200,
                                                      convergenceMinimumValue=1e-5,
                                                      convergenceWindowSize=5)
            R.SetInitialTransform(sitk.TranslationTransform(fixed.GetDimension()))
            R.SetInterpolator(sitk.sitkLinear)
            R.AddCommand(sitk.sitkIterationEvent, lambda: self.command_iteration(R))

            outTx = R.Execute(fixed, moving)

            self.runPrint(outTx, R)

            resImage = self.reSample(fixed, outTx, moving, 1)
            resName = fixFiles[index].split(".", 1)[0] + '_reg2'
            GUI().writeImage(resImage[0], resImage[1], resImage[2], resName)

    def registration_3(self):    # 2D registration

        num = GUI().initImage()[0]
        fixFiles = GUI().initImage()[1]
        moveFiles = GUI().initImage()[2]
        fixDir = GUI().initImage()[3]
        moveDir = GUI().initImage()[4]
        #pixelType = sitk.sitkFloat32

        for index in range(num):
            fixed = sitk.ReadImage(os.path.join(fixDir, fixFiles[index]), sitk.sitkFloat32)
            moving = sitk.ReadImage(os.path.join(moveDir, moveFiles[index]), sitk.sitkFloat32)

            R = sitk.ImageRegistrationMethod()
            R.SetMetricAsCorrelation()
            R.SetOptimizerAsRegularStepGradientDescent(learningRate=2.0,
                                                       minStep=1e-4,
                                                       numberOfIterations=500,
                                                       gradientMagnitudeTolerance=1e-8)
            R.SetOptimizerScalesFromIndexShift()
            tx = sitk.CenteredTransformInitializer(fixed, moving, sitk.Similarity2DTransform())
            R.SetInitialTransform(tx)
            R.SetInterpolator(sitk.sitkLinear)
            R.AddCommand(sitk.sitkIterationEvent, lambda: self.command_iteration(R))

            outTx = R.Execute(fixed, moving)

            self.runPrint(outTx, R)

            resImage = self.reSample(fixed, outTx, moving, 1)
            resName = fixFiles[index].split(".", 1)[0] + '_reg3'
            GUI().writeImage(resImage[0], resImage[1], resImage[2], resName)


    def registration_4(self):

        num = GUI().initImage()[0]
        fixFiles = GUI().initImage()[1]
        moveFiles = GUI().initImage()[2]
        fixDir = GUI().initImage()[3]
        moveDir = GUI().initImage()[4]

        for index in range(num):

            fixed = sitk.ReadImage(os.path.join(fixDir, fixFiles[index]), sitk.sitkFloat32)
            moving = sitk.ReadImage(os.path.join(moveDir, moveFiles[index]), sitk.sitkFloat32)

            numberOfBins = 24
            samplingPercentage = 0.10

            if len(sys.argv) > 4:
                numberOfBins = int(sys.argv[4])
            if len(sys.argv) > 5:
                samplingPercentage = float(sys.argv[5])

            R = sitk.ImageRegistrationMethod()
            R.SetMetricAsMattesMutualInformation(numberOfBins)
            R.SetMetricSamplingPercentage(samplingPercentage, sitk.sitkWallClock)
            R.SetMetricSamplingStrategy(R.RANDOM)
            R.SetOptimizerAsRegularStepGradientDescent(1.0, .001, 200)
            R.SetInitialTransform(sitk.TranslationTransform(fixed.GetDimension()))
            R.SetInterpolator(sitk.sitkLinear)
            R.AddCommand(sitk.sitkIterationEvent, lambda: self.command_iteration(R))

            outTx = R.Execute(fixed, moving)

            self.runPrint(outTx, R)

            resImage = self.reSample(fixed, outTx, moving, 100)
            resName = fixFiles[index].split(".",1)[0] + '_reg4'
            GUI().writeImage(resImage[0], resImage[1], resImage[2], resName)

    def registrationBSpline_1(self):   # initial waring

        num = GUI().initImage()[0]
        fixFiles = GUI().initImage()[1]
        moveFiles = GUI().initImage()[2]
        fixDir = GUI().initImage()[3]
        moveDir = GUI().initImage()[4]

        for index in range(num):

            fixed = sitk.ReadImage(os.path.join(fixDir, fixFiles[index]), sitk.sitkFloat32)
            moving = sitk.ReadImage(os.path.join(moveDir, moveFiles[index]), sitk.sitkFloat32)

            transformDomainMeshSize = [8] * moving.GetDimension()
            tx = sitk.BSplineTransformInitializer(fixed,
                                                  transformDomainMeshSize)

            print("Initial Parameters:");
            print(tx.GetParameters())

            R = sitk.ImageRegistrationMethod()
            R.SetMetricAsCorrelation()

            R.SetOptimizerAsLBFGSB(gradientConvergenceTolerance=1e-5,
                                   numberOfIterations=100,
                                   maximumNumberOfCorrections=5,
                                   maximumNumberOfFunctionEvaluations=1000,
                                   costFunctionConvergenceFactor=1e+7)
            R.SetInitialTransform(tx, True)
            R.SetInterpolator(sitk.sitkLinear)

            R.AddCommand(sitk.sitkIterationEvent, lambda: self.command_bs_iteration(R))

            outTx = R.Execute(fixed, moving)

            resImage = self.reSample(fixed, outTx, moving, 100)
            resName = fixFiles[index].split(".", 1)[0] + '_regBS1'
            GUI().writeImage(resImage[0], resImage[1], resImage[2], resName)

    def registrationBSpline_2(self):

        num = GUI().initImage()[0]
        fixFiles = GUI().initImage()[1]
        moveFiles = GUI().initImage()[2]
        fixDir = GUI().initImage()[3]
        moveDir = GUI().initImage()[4]

        for index in range(num):

            fixed = sitk.ReadImage(os.path.join(fixDir,fixFiles[index]), sitk.sitkFloat32)
            moving = sitk.ReadImage(os.path.join(moveDir,moveFiles[index]), sitk.sitkFloat32)

            transformDomainMeshSize = [10] * moving.GetDimension()
            tx = sitk.BSplineTransformInitializer(fixed,
                                                  transformDomainMeshSize)
            print("Initial Parameters:");
            print(tx.GetParameters())
            R = sitk.ImageRegistrationMethod()
            R.SetMetricAsMattesMutualInformation(50)
            R.SetOptimizerAsGradientDescentLineSearch(5.0, 100,
                                                      convergenceMinimumValue=1e-4,
                                                      convergenceWindowSize=5)
            R.SetOptimizerScalesFromPhysicalShift()
            R.SetInitialTransform(tx)
            R.SetInterpolator(sitk.sitkLinear)
            R.SetShrinkFactorsPerLevel([6, 2, 1])
            R.SetSmoothingSigmasPerLevel([6, 2, 1])
            R.AddCommand(sitk.sitkIterationEvent, lambda: self.command_bs_iteration(R))

            outTx = R.Execute(fixed, moving)

            self.runPrint(outTx, R)

            resImage = self.reSample(fixed, outTx, moving, 100)
            resName = fixFiles[index].split(".", 1)[0] + '_regBS2'
            GUI().writeImage(resImage[0], resImage[1], resImage[2], resName)

    def registrationBSpline_3(self):

        num = GUI().initImage()[0]
        fixFiles = GUI().initImage()[1]
        moveFiles = GUI().initImage()[2]
        fixDir = GUI().initImage()[3]
        moveDir = GUI().initImage()[4]

        for index in range(num):

            fixed = sitk.ReadImage(os.path.join(fixDir, fixFiles[index]), sitk.sitkFloat32)
            moving = sitk.ReadImage(os.path.join(moveDir, moveFiles[index]), sitk.sitkFloat32)

            transformDomainMeshSize = [2] * fixed.GetDimension()
            tx = sitk.BSplineTransformInitializer(fixed,
                                                  transformDomainMeshSize)

            print("Initial Number of Parameters: {0}".format(tx.GetNumberOfParameters()))

            R = sitk.ImageRegistrationMethod()
            R.SetMetricAsJointHistogramMutualInformation()
            R.SetOptimizerAsGradientDescentLineSearch(5.0,
                                                      100,
                                                      convergenceMinimumValue=1e-4,
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
            resName = fixFiles[index].split(".", 1)[0] + '_regBS3'
            GUI().writeImage(resImage[0], resImage[1], resImage[2], resName)

    def registrationDisplacement(self):

        num = GUI().initImage()[0]
        fixFiles = GUI().initImage()[1]
        moveFiles = GUI().initImage()[2]
        fixDir = GUI().initImage()[3]
        moveDir = GUI().initImage()[4]

        for index in range(num):

            fixed = sitk.ReadImage(os.path.join(fixDir,fixFiles[index]), sitk.sitkFloat32)
            moving = sitk.ReadImage(os.path.join(moveDir,moveFiles[index]), sitk.sitkFloat32)

            initialTx = sitk.CenteredTransformInitializer(fixed, moving, sitk.AffineTransform(fixed.GetDimension()))
            R = sitk.ImageRegistrationMethod()
            R.SetShrinkFactorsPerLevel([3, 2, 1])
            R.SetSmoothingSigmasPerLevel([2, 1, 1])
            R.SetMetricAsJointHistogramMutualInformation(20)
            R.MetricUseFixedImageGradientFilterOff()
            R.SetOptimizerAsGradientDescent(learningRate=1.0,
                                            numberOfIterations=100,
                                            estimateLearningRate=R.EachIteration)
            R.SetOptimizerScalesFromPhysicalShift()
            R.SetInitialTransform(initialTx, inPlace=True)
            R.SetInterpolator(sitk.sitkLinear)
            R.AddCommand(sitk.sitkIterationEvent, lambda: self.command_ds_iteration(R))
            #R.AddCommand(sitk.sitkMultiResolutionIterationEvent, lambda: command_multiresolution_iteration(R))

            outTx = R.Execute(fixed, moving)

            self.runPrint(outTx, R)

            displacementField = sitk.Image(fixed.GetSize(), sitk.sitkVectorFloat64)
            displacementField.CopyInformation(fixed)
            displacementTx = sitk.DisplacementFieldTransform(displacementField)
            del displacementField
            displacementTx.SetSmoothingGaussianOnUpdate(varianceForUpdateField=0.0,
                                                        varianceForTotalField=1.5)
            R.SetMovingInitialTransform(outTx)
            R.SetInitialTransform(displacementTx, inPlace=True)
            R.SetMetricAsANTSNeighborhoodCorrelation(4)
            R.MetricUseFixedImageGradientFilterOff()
            R.SetShrinkFactorsPerLevel([3, 2, 1])
            R.SetSmoothingSigmasPerLevel([2, 1, 1])
            R.SetOptimizerScalesFromPhysicalShift()
            R.SetOptimizerAsGradientDescent(learningRate=1,
                                            numberOfIterations=300,
                                            estimateLearningRate=R.EachIteration)
            outTx.AddTransform(R.Execute(fixed, moving))

            self.runPrint(outTx, R)

            resImage = self.reSample(fixed, outTx, moving, 100)
            resName = fixFiles[index].split(".", 1)[0] + '_regD'
            GUI().writeImage(resImage[0], resImage[1], resImage[2], resName)

    def registrationExhaustive(self):

        num = GUI().initImage()[0]
        fixFiles = GUI().initImage()[1]
        moveFiles = GUI().initImage()[2]
        fixDir = GUI().initImage()[3]
        moveDir = GUI().initImage()[4]

        for index in range(num):

            fixed = sitk.ReadImage(os.path.join(fixDir,fixFiles[index]), sitk.sitkFloat32)
            moving = sitk.ReadImage(os.path.join(moveDir,moveFiles[index]), sitk.sitkFloat32)

            R = sitk.ImageRegistrationMethod()

            R.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)

            sample_per_axis = 12

            tx = sitk.Euler3DTransform()
            R.SetOptimizerAsExhaustive([sample_per_axis//2, sample_per_axis//2, sample_per_axis//4, 0, 0, 0])
            R.SetOptimizerScales(
                    [2.0*pi/sample_per_axis, 2.0*pi/sample_per_axis, 2.0*pi/sample_per_axis, 1.0, 1.0, 1.0])

            # Initialize the transform with a translation and the center of
            # rotation from the moments of intensity.
            tx = sitk.CenteredTransformInitializer(fixed, moving, tx)
            R.SetInitialTransform(tx)
            R.SetInterpolator(sitk.sitkLinear)
            R.AddCommand(sitk.sitkIterationEvent, lambda: self.command_iteration(R))

            outTx = R.Execute(fixed, moving)

            self.runPrint(outTx, R)

            resImage = self.reSample(fixed, outTx, moving, 1)
            resName = fixFiles[index].split(".", 1)[0] + '_regE'
            GUI().writeImage(resImage[0], resImage[1], resImage[2], resName)