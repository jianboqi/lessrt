package less.gui.lidar.model;

public class BeamParameterModel extends Model {
	public double axialDivision;
	public int maxOrder;
	
	public BeamParameterModel() {
		axialDivision = 100;
		maxOrder = 2;
		
		setLabel("axialDivision", "Axial division");
		setLabel("maxOrder", "Max scattering order");
	}

	public double getAxialDivision() {
		return axialDivision;
	}

	public void setAxialDivision(double axialDivision) {
		this.axialDivision = axialDivision;
	}

	public int getMaxOrder() {
		return maxOrder;
	}

	public void setMaxOrder(int maxOrder) {
		this.maxOrder = maxOrder;
	}
	
	
}
