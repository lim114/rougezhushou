def show_barrier_ledger(self):
        panel=self.offline_tools
        panel.family.setCurrentIndex(panel.family.findData('calibration'))
        panel.query.setCurrentIndex(panel.query.findData('barrier-ledger'))
        self.centralWidget().setCurrentWidget(panel)

def show_shield_grants(self):
        self.offline_tools.select_query('calibration','shield-grants')
        self.centralWidget().setCurrentWidget(self.offline_tools)

def show_shield_inventory(self):
        self.offline_tools.select_query('calibration','shield-inventory')
        self.centralWidget().setCurrentWidget(self.offline_tools)

def show_explosion_values(self):
        self.offline_tools.select_query('calibration','explosion-values')
        self.centralWidget().setCurrentWidget(self.offline_tools)
