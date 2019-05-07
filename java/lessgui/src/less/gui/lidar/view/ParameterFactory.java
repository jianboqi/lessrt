package less.gui.lidar.view;

import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Pane;
import less.gui.lidar.model.Model;

public class ParameterFactory {
	
	public static Pane createTextParameter(String name, Model model, double... args) {
		HBox box = new HBox();
		Label label = new Label();
		TextField field = new TextField();
		
		box.getChildren().addAll(label, field);
		label.setPrefWidth(300);
//		label.setPrefWidth(100);
		
		label.setText(model.getLabel(name));
		field.setText(model.getField(name).toString());
		
		if (args.length > 0) {
			label.setPrefWidth(args[0]);
		}
		if (args.length > 1) {
			field.setPrefWidth(args[1]);	
		}
	
		field.textProperty().addListener((ov, o, newValue) -> {
			try {
				double value = Double.parseDouble(newValue);
				model.setField(name, value);
			} catch (Exception e) {
				e.printStackTrace();
			}
		});	
		
		return box;
	}
}
