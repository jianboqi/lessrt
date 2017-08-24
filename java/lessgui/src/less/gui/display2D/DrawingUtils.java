package less.gui.display2D;

import javafx.scene.canvas.GraphicsContext;
import javafx.scene.paint.Color;
import javafx.scene.transform.Affine;
import javafx.scene.transform.Transform;

public class DrawingUtils {
	public static void drawArrow(GraphicsContext gc, double x1, double y1, double x2, double y2) {
//	    gc.setFill(Color.BLACK);
	    int ARR_SIZE = 8;
	    double dx = x2 - x1, dy = y2 - y1;
	    double angle = Math.atan2(dy, dx);
	    int len = (int) Math.sqrt(dx * dx + dy * dy);

	    Transform transform = Transform.translate(x1, y1);
	    transform = transform.createConcatenation(Transform.rotate(Math.toDegrees(angle), 0, 0));
	    gc.setTransform(new Affine(transform));

	    gc.strokeLine(0, 0, len, 0);
	    gc.fillPolygon(new double[]{len, len - ARR_SIZE, len - ARR_SIZE, len}, new double[]{0, -ARR_SIZE, ARR_SIZE, 0},
	            4);
	    gc.setTransform(new Affine());
	}
}
