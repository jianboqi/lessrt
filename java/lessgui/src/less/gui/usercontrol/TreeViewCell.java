package less.gui.usercontrol;

import javafx.scene.control.Label;
import javafx.scene.control.TreeCell;
import javafx.scene.layout.AnchorPane;
import less.gui.model.TreeViewNode;

public class TreeViewCell extends TreeCell<TreeViewNode>{
	private  AnchorPane anchorPane;
	private  Label label;

	public TreeViewCell() {
//	anchorPane = new AnchorPane();
//	label = new Label();
//	anchorPane.getChildren().addAll(label);
//	anchorPane.setStyle("-fx-border-color: gray");
//	anchorPane.setPadding(new Insets(5));
//	AnchorPane.setLeftAnchor(label, 15.0);
	}

	@Override
	public void updateItem(TreeViewNode item, boolean empty) {
		super.updateItem(item, empty);
		if (empty) {
			setText(null);
			setGraphic(null);
		} else {
			setText(item.getParameterName());
//			label.setText(item.getStatus());
//			setGraphic(anchorPane);
		}
	}
}
