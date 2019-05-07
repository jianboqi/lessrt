package less.gui.lidar.model;

public class DeviceParameterModel extends Model {
	public double sensorArea;
	public double footprintHalfAngle;
	public double halfFov;
	public double pulseEnergy;
	public double acquisitionPeriod;
	public double halfDurationNumberOfSigma;
	public double halfPulseDurationAtHalfPeak;
	public double fractionAtRadius;
	
	public DeviceParameterModel() {
		this.sensorArea = 0.1;
		this.footprintHalfAngle = 0.0012;
		this.halfFov = 0.0015;
		this.pulseEnergy = 1;
		this.acquisitionPeriod = 1;
		this.halfDurationNumberOfSigma = 3;
		this.halfPulseDurationAtHalfPeak = 2;
		this.fractionAtRadius = 0.368;
		
		setLabel("sensorArea", "Sensor area [m^2]");
		setLabel("footprintHalfAngle", "Footprint half angle [rad]");
		setLabel("halfFov", "FOV half angle [rad]");
		setLabel("pulseEnergy", "Pulse energy [mJ]");
		setLabel("acquisitionPeriod", "Acquisition rate (Period) [ns]");
		setLabel("halfDurationNumberOfSigma", "Half duration [Number of sigma]");
		setLabel("halfPulseDurationAtHalfPeak", "Half pulse duration at half peak [ns]");
		setLabel("fractionAtRadius", "Fraction at radius");	
	}
	
	public void setSensorArea(double sensorArea) {
		this.sensorArea = sensorArea;
	}

	public void setFootprintHalfAngle(double footprintHalfAngle) {
		this.footprintHalfAngle = footprintHalfAngle;
	}

	public void setHalfFov(double halfFov) {
		this.halfFov = halfFov;
	}

	public void setPulseEnergy(double pulseEnergy) {
		this.pulseEnergy = pulseEnergy;
	}

	public void setAcquisitionPeriod(double acquisitionPeriod) {
		this.acquisitionPeriod = acquisitionPeriod;
	}

	public void setHalfDurationNumberOfSigma(double halfDurationNumberOfSigma) {
		this.halfDurationNumberOfSigma = halfDurationNumberOfSigma;
	}

	public void setHalfPulseDurationAtHalfPeak(double halfPulseDurationAtHalfPeak) {
		this.halfPulseDurationAtHalfPeak = halfPulseDurationAtHalfPeak;
	}

	public void setFractionAtRadius(double fractionAtRadius) {
		this.fractionAtRadius = fractionAtRadius;
	}

	public double getSensorArea() {
		return sensorArea;
	}

	public double getFootprintHalfAngle() {
		return footprintHalfAngle;
	}

	public double getHalfFov() {
		return halfFov;
	}

	public double getPulseEnergy() {
		return pulseEnergy;
	}

	public double getAcquisitionPeriod() {
		return acquisitionPeriod;
	}

	public double getHalfDurationNumberOfSigma() {
		return halfDurationNumberOfSigma;
	}

	public double getHalfPulseDurationAtHalfPeak() {
		return halfPulseDurationAtHalfPeak;
	}

	public double getFractionAtRadius() {
		return fractionAtRadius;
	}
}
