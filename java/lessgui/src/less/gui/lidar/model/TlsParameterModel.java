package less.gui.lidar.model;

public class TlsParameterModel extends Model {
	public double x;
	public double y;
	public double z;
	public double centerZenith;
	public double deltaZenith;
	public double resolutionZenith;
	public double centerAzimuth;
	public double deltaAzimuth;
	public double resolutionAzimuth;
	
	public double minRange;
	public double maxRange;
	
	public TlsParameterModel() {
		x = 20;                 
		y = 20;                 
		z = 10;                 
		centerZenith = 90;      
		deltaZenith = 10;       
		resolutionZenith = 1;  
		centerAzimuth = 45;     
		deltaAzimuth = 10;      
		resolutionAzimuth = 1; 
		                   
		minRange = 10;
		maxRange = 100;  
		
		setLabel("x", "TLS position X [m]");                 
		setLabel("y", "TLS position Y [m]");                 
		setLabel("z", "TLS position Z [m]");                 
		setLabel("centerZenith", "Center zenith [deg]");      
		setLabel("deltaZenith", "Delta zenith [deg]");       
		setLabel("resolutionZenith", "Resolution zenith [deg]");  
		setLabel("centerAzimuth", "Center azimuth [deg]");     
		setLabel("deltaAzimuth", "Delta azimuth [deg]");      
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

	public double getCenterZenith() {
		return centerZenith;
	}

	public void setCenterZenith(double centerZenith) {
		this.centerZenith = centerZenith;
	}

	public double getDeltaZenith() {
		return deltaZenith;
	}

	public void setDeltaZenith(double deltaZenith) {
		this.deltaZenith = deltaZenith;
	}

	public double getResolutionZenith() {
		return resolutionZenith;
	}

	public void setResolutionZenith(double resolutionZenith) {
		this.resolutionZenith = resolutionZenith;
	}

	public double getCenterAzimuth() {
		return centerAzimuth;
	}

	public void setCenterAzimuth(double centerAzimuth) {
		this.centerAzimuth = centerAzimuth;
	}

	public double getDeltaAzimuth() {
		return deltaAzimuth;
	}

	public void setDeltaAzimuth(double deltaAzimuth) {
		this.deltaAzimuth = deltaAzimuth;
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
