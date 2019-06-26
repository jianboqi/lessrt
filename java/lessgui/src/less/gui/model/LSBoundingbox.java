package less.gui.model;

import javafx.beans.Observable;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.geometry.BoundingBox;

public class LSBoundingbox {
	public double 
			minX=Double.POSITIVE_INFINITY, 
			minY=Double.POSITIVE_INFINITY, 
			minZ=Double.POSITIVE_INFINITY, 
			maxX=Double.NEGATIVE_INFINITY, 
			maxY=Double.NEGATIVE_INFINITY, 
			maxZ=Double.NEGATIVE_INFINITY;
	
	
	private ObservableList<LSBoundingbox> childBoundingbox = FXCollections.observableArrayList();
	
//	public LSBoundingbox(double minX, double minY, double minZ, double maxX, double maxY, double maxZ) {
//		this.minX = minX;
//		this.minY = minY;
//		this.minZ = minZ;
//		this.maxX = maxX;
//		this.maxY = maxY;
//		this.maxZ = maxZ;
//	}
	
	public LSBoundingbox(){
		childBoundingbox.addListener((Observable observable) -> {
			updateBoundingbox();
	    });
	}
	
	
	public void reset(){
		this.minX=Double.POSITIVE_INFINITY;
		this.minY=Double.POSITIVE_INFINITY;
		this.minZ=Double.POSITIVE_INFINITY; 
		this.maxX=Double.NEGATIVE_INFINITY; 
		this.maxY=Double.NEGATIVE_INFINITY; 
		this.maxZ=Double.NEGATIVE_INFINITY;
	}
	
	public void updateBoundingbox(){
		this.reset();
		for(int i=0;i<this.childBoundingbox.size();i++){
			LSBoundingbox child = this.childBoundingbox.get(i);
			this.minX = Math.min(this.minX, child.minX);
			this.minY = Math.min(this.minY, child.minY);
			this.minZ = Math.min(this.minZ, child.minZ);
			this.maxX = Math.max(this.maxX, child.maxX);
			this.maxY = Math.max(this.maxY, child.maxY);
			this.maxZ = Math.max(this.maxZ, child.maxZ);
		}
	}
	
	public LSBoundingbox getOffsetedBoundingbox(double x, double y, double z) {
		LSBoundingbox newboundingbox = new LSBoundingbox();
		newboundingbox.minX = minX+x;
		newboundingbox.minY = minY+y;
		newboundingbox.minZ = minZ+z;
		newboundingbox.maxX = maxX+x;
		newboundingbox.maxY = maxY+y;
		newboundingbox.maxZ = maxZ+z;
		return newboundingbox;
	}
	
	public void offset(double x, double y, double z) {
		for(int i=0;i<this.childBoundingbox.size();i++){
			LSBoundingbox child = this.childBoundingbox.get(i);
			child.minX = child.minX+x;
			child.minY = child.minY+y;
			child.minZ = child.minZ+z;
			child.maxX = child.maxX+x;
			child.maxY = child.maxY+y;
			child.maxZ = child.maxZ+z;
		}
		updateBoundingbox();
	}
	
	/**
	 * merge boundingbox
	 * @param bound1
	 * @param bound2
	 * @return
	 */
	public static LSBoundingbox merge(LSBoundingbox bound1, LSBoundingbox bound2){
		LSBoundingbox newboundingbox = new LSBoundingbox();
		newboundingbox.minX = Math.min(bound1.minX, bound2.minX);
		newboundingbox.minY = Math.min(bound1.minY, bound2.minY);
		newboundingbox.minZ = Math.min(bound1.minZ, bound2.minZ);
		newboundingbox.maxX = Math.max(bound1.maxX, bound2.maxX);
		newboundingbox.maxY = Math.max(bound1.maxY, bound2.maxY);
		newboundingbox.maxZ = Math.max(bound1.maxZ, bound2.maxZ);
		return newboundingbox;
	}
	
	/**
	 * Merge children from another Boundingbox
	 * @param bound1
	 */
	public void mergeAllChildren(LSBoundingbox bound1) {
		for(int i=0;i<bound1.getChildList().size();i++){
			LSBoundingbox child = bound1.getChildList().get(i);
			this.childBoundingbox.add(child);
		}
	}
	
	public ObservableList<LSBoundingbox> getChildList(){
		return this.childBoundingbox;
	}
	
	public double getMaxDiameter(){
		return Math.max(this.maxX-this.minX, this.maxZ-this.minZ);
	}
	
	public double getMaxOfAllAxes(){
		return Math.max(getMaxDiameter(), this.maxY-this.minY);
	}
	
	public double getHeight(){
		return this.maxY - this.minY;
	}
	
	public double getXExtent(){
		return this.maxX-this.minX;
	}
	
	public double getYExtent(){
		return this.maxZ-this.minZ;
	}
	
	public String toString(){
		String totalStr = "";
		for(int i=0;i<this.childBoundingbox.size();i++){
			LSBoundingbox child = this.childBoundingbox.get(i);
			totalStr += child.minX + " ";
			totalStr += child.minY + " ";
			totalStr += child.minZ + " ";
			totalStr += child.maxX + " ";
			totalStr += child.maxY + " ";
			totalStr += child.maxZ + " ";
		}
		return totalStr.substring(0, totalStr.length()-1);
	}
	
	public void removeChild(int index){
		this.childBoundingbox.remove(index);
	}
	
	public void addChild(LSBoundingbox child){
		this.childBoundingbox.add(child);
	}
	
	public void loadFromString(String str){
		String [] arr = str.trim().split(" ");
		
		for(int i=0;i<arr.length;i += 6){
			LSBoundingbox newboundingbox = new LSBoundingbox();
			newboundingbox.minX = Double.parseDouble(arr[i]);
			newboundingbox.minY = Double.parseDouble(arr[i+1]);
			newboundingbox.minZ = Double.parseDouble(arr[i+2]);
			newboundingbox.maxX = Double.parseDouble(arr[i+3]);
			newboundingbox.maxY = Double.parseDouble(arr[i+4]);
			newboundingbox.maxZ = Double.parseDouble(arr[i+5]);
			this.childBoundingbox.add(newboundingbox);
		}
	}
	
}
