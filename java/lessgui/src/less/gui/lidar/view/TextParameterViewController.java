package less.gui.lidar.view;

import java.lang.reflect.Field;

import javafx.geometry.Insets;
import javafx.scene.layout.AnchorPane;
import javafx.scene.layout.Pane;
import javafx.scene.layout.VBox;
import less.gui.lidar.model.Model;

public class TextParameterViewController {
	public AnchorPane parameterAnchorPane;
	private VBox parameterVBox;
	private Model model;
	
	public TextParameterViewController(Model model) {
		parameterAnchorPane = new AnchorPane();
		parameterVBox = new VBox();
		parameterVBox.setSpacing(10);
		parameterVBox.setPadding(new Insets(20,0,0,0));
		
		parameterAnchorPane.getChildren().add(parameterVBox);
		this.model = model;
		
		addParameter();
	}
	
	private void addParameter() {
		try {
//			for (String field : model.labelMap.keySet()) {
//				Pane box = ParameterFactory.createTextParameter(field, model, 210, 100);
//				parameterVBox.getChildren().add(box);
//			}
			
			for (Field field : model.getClass().getDeclaredFields()) {
				if (field.getName().equals("labelMap")) {
					continue;
				}
				Pane box = ParameterFactory.createTextParameter(field.getName(), model, 300, 100);
				parameterVBox.getChildren().add(box);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public void setModel(Model model) {
		this.model = model;
	}
	
	
}
