package less.gui.lidar.model;

public class AlsParameterModel extends Model {
	public double altitude;
	public double platformAzimuth;
	public double swathWidth;
	public double startX;
	public double startY;
	public double endX;
	public double endY;
	public double azimuthResolution;
	public double rangeResolution;
	
	public double savedUpper;
	public double savedLower;
	
	public AlsParameterModel() {
		altitude = 10;
		platformAzimuth = 0;
		swathWidth = 30;
		startX = 5;
		startY = 20;
		endX = 35;
		endY = 20;
		azimuthResolution = 3;
		rangeResolution = 3;
		
		savedUpper = 10;
		savedLower = 10;
		
		setLabel("altitude", "Altitude [km]");
		setLabel("platformAzimuth", "Platform azimuth [deg]");
		setLabel("swathWidth", "Swath width [m]");
		setLabel("startX", "Start X [m]");
		setLabel("startY", "Start Y [m]");
		setLabel("endX", "End X [m]");
		setLabel("endY", "End Y [m]");
		setLabel("azimuthResolution", "Azimuth resolution [m]");
		setLabel("rangeResolution", "Range resolution [m]");
		
		setLabel("savedUpper", "Saved range above scene bottom [m]");
		setLabel("savedLower", "Saved range below scene bottom [m]");
	}

	public double getAltitude() {
		return altitude;
	}

	public void setAltitude(double altitude) {
		this.altitude = altitude;
	}

	public double getPlatformAzimuth() {
		return platformAzimuth;
	}

	public void setPlatformAzimuth(double platformAzimuth) {
		this.platformAzimuth = platformAzimuth;
	}

	public double getSwathWidth() {
		return swathWidth;
	}

	public void setSwathWidth(double swathWidth) {
		this.swathWidth = swathWidth;
	}

	public double getStartX() {
		return startX;
	}

	public void setStartX(double startX) {
		this.startX = startX;
	}

	public double getStartY() {
		return startY;
	}

	public void setStartY(double startY) {
		this.startY = startY;
	}

	public double getEndX() {
		return endX;
	}

	public void setEndX(double endX) {
		this.endX = endX;
	}

	public double getEndY() {
		return endY;
	}

	public void setEndY(double endY) {
		this.endY = endY;
	}

	public double getAzimuthResolution() {
		return azimuthResolution;
	}

	public void setAzimuthResolution(double azimuthResolution) {
		this.azimuthResolution = azimuthResolution;
	}

	public double getRangeResolution() {
		return rangeResolution;
	}

	public void setRangeResolution(double rangeResolution) {
		this.rangeResolution = rangeResolution;
	}

	public double getSavedUpper() {
		return savedUpper;
	}

	public void setSavedUpper(double savedUpper) {
		this.savedUpper = savedUpper;
	}

	public double getSavedLower() {
		return savedLower;
	}

	public void setSavedLower(double savedLower) {
		this.savedLower = savedLower;
	}
	
	
}
