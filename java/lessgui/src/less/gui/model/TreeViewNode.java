package less.gui.model;

import javafx.beans.property.SimpleStringProperty;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import less.gui.usercontrol.HierarchyData;


public class TreeViewNode implements HierarchyData<TreeViewNode>{
	private  SimpleStringProperty parameterName;
	private  SimpleStringProperty parameterType;
	
	private final ObservableList<TreeViewNode> children = FXCollections.observableArrayList();

	public TreeViewNode(String parameterName, String parameterType) {
		this.parameterName = new SimpleStringProperty(parameterName);
		this.parameterType = new SimpleStringProperty(parameterType);
	}
	
	public String getParameterName(){
		return parameterName.get();
	}
	
	public void setParameterName(String name){
		this.parameterName.set(name);
	}
	
	public String getParameterType(){
		return parameterType.get();
	}
	
	public void setParameterType(String type){
		this.parameterType.set(type);
	}
	
	@Override
	public ObservableList<TreeViewNode> getChildren() {
		return children;
	}
	
	
	
}
