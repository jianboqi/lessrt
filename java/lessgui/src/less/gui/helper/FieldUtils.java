package less.gui.helper;

import java.lang.reflect.Field;

import com.sun.javafx.scene.control.skin.ScrollPaneSkin;

import javafx.scene.Node;
import javafx.scene.control.ScrollPane;
import javafx.scene.layout.StackPane;

public class FieldUtils {

    public static void fixBlurryText(Node node) {
        try {
            Field field = ScrollPaneSkin.class.getDeclaredField("viewRect");
            field.setAccessible(true);

            ScrollPane scrollPane = (ScrollPane) node.lookup(".scroll-pane");

            StackPane stackPane = (StackPane) field.get(scrollPane.getSkin());
            stackPane.setCache(false);

        } catch (NoSuchFieldException | SecurityException |  IllegalAccessException e) {
            e.printStackTrace();
        }
    }
}
