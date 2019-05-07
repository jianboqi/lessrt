package less.gui.lidar.model;

public class MonoPulseParameterModel extends Model {
	public double x;
	public double y;
	public double z;
	public double zenith;
	public double azimuth;
	
	public double minRange;
	public double maxRange;
	
	public MonoPulseParameterModel() {
		x = 20;                 
		y = 20;                 
		z = 100; 
		azimuth = 0;
		zenith = 0;
		            
		minRange = 90;
		maxRange = 110;  
		
		setLabel("x", "X [m]");                 
		setLabel("y", "Y [m]");                 
		setLabel("z", "Z [m]");    
		setLabel("zenith", "Zenith [deg]");
		setLabel("azimuth", "Azimuth [deg]");
                
		setLabel("minRange", "Min Range [m]");
		setLabel("maxRange", "Max Range [m]");          
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

	public double getZenith() {
		return zenith;
	}

	public void setZenith(double zenith) {
		this.zenith = zenith;
	}

	public double getAzimuth() {
		return azimuth;
	}

	public void setAzimuth(double azimuth) {
		this.azimuth = azimuth;
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
