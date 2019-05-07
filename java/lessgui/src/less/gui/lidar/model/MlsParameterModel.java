package less.gui.lidar.model;

public class MlsParameterModel extends Model {
	public double x;
	public double y;
	public double z;
	public double axisZenith;
	public double axisAzimuth;
	public int numberOfLines;
	public double resolutionZenith;
	public double resolutionAzimuth;
	
	public double minRange;
	public double maxRange;
	
	public MlsParameterModel() {
		x = 20;                 
		y = 20;                 
		z = 10;          
		axisZenith = 0;
		axisAzimuth = 0;
		numberOfLines = 8;
		resolutionZenith = 1;   
		resolutionAzimuth = 1; 
		                  
		minRange = 10;
		maxRange = 100;  
		
		setLabel("x", "MLS position X [m]");                 
		setLabel("y", "MLS position Y [m]");                 
		setLabel("z", "MLS position Z [m]");    
		setLabel("axisZenith", "Axis zenith [deg]");
		setLabel("axisAzimuth", "Axis azimuth [deg]");
		setLabel("numberOfLines", "Number of lines");
		setLabel("resolutionZenith", "Resolution zenith [deg]");   
		setLabel("resolutionAzimuth", "Resolution azimuth [deg]"); 
                
		setLabel("minRange", "Min range [m]");
		setLabel("maxRange", "Max range [m]");          
	}

	public double getX() {
		return x;
	}

	public void setX(double x) {
		this.x = x;
	}

	public double getY() {
		return y;
	}

	public void setY(double y) {
		this.y = y;
	}

	public double getZ() {
		return z;
	}

	public void setZ(double z) {
		this.z = z;
	}

	public double getAxisZenith() {
		return axisZenith;
	}

	public void setAxisZenith(double axisZenith) {
		this.axisZenith = axisZenith;
	}

	public double getAxisAzimuth() {
		return axisAzimuth;
	}

	public void setAxisAzimuth(double axisAzimuth) {
		this.axisAzimuth = axisAzimuth;
	}

	public int getNumberOfLines() {
		return numberOfLines;
	}

	public void setNumberOfLines(int numberOfLines) {
		this.numberOfLines = numberOfLines;
	}

	public double getResolutionZenith() {
		return resolutionZenith;
	}

	public void setResolutionZenith(double resolutionZenith) {
		this.resolutionZenith = resolutionZenith;
	}

	public double getResolutionAzimuth() {
		return resolutionAzimuth;
	}

	public void setResolutionAzimuth(double resolutionAzimuth) {
		this.resolutionAzimuth = resolutionAzimuth;
	}

	public double getMinRange() {
		return minRange;
	}

	public void setMinRange(double minRange) {
		this.minRange = minRange;
	}

	public double getMaxRange() {
		return maxRange;
	}

	public void setMaxRange(double maxRange) {
		this.maxRange = maxRange;
	}
	
	
}
