

class StartupPanelMeasurement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def test_measure_existing_eight_constructors_without_changing_product_code(self):
        from rouge.offline_tools_view import OfflineToolsPanel
        from rouge.paired_calibration_view import PairedCalibrationPanel
        from rouge.attack_state_sequence_view import AttackStateSequencePanel
        from rouge.timing_calibration_view import TimingCalibrationPanel
        from rouge.bounded_calibration_view import BoundedCalibrationPanel
        from rouge.calibration_experiment_view import CalibrationExperimentPanel
        from rouge.recipient_native_ratio_view import RecipientNativeRatioPanel
        from rouge.relic_order_precision_view import RelicOrderPrecisionPanel
        for cls in(OfflineToolsPanel,PairedCalibrationPanel,AttackStateSequencePanel,TimingCalibrationPanel,BoundedCalibrationPanel,CalibrationExperimentPanel,RecipientNativeRatioPanel,RelicOrderPrecisionPanel):
            original=cls.__init__
            def measured(obj,*a,_original=original,_name=cls.__name__,**kw):
                start=time.perf_counter();_original(obj,*a,**kw);PROFILE.append({'class':_name,'constructor_seconds':time.perf_counter()-start})
            self.enterContext(patch.object(cls,'__init__',measured))
        fixture.StateCalculationUpdateTests.setUp(self)
        self.assertEqual(len(PROFILE),8)

