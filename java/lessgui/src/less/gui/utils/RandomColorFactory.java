package less.gui.utils;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;

import javafx.scene.paint.Color;

public class RandomColorFactory {
	private int currentIndex = 0;
	private ArrayList<Color> colors;
	
	private static String[] all_standard_colors={"#9c513b",
"#4c5fcd",
"#61b63a",
"#c566df",
"#abb732",
"#8845b3",
"#44bb6a",
"#b636a5",
"#85af59",
"#9273e8",
"#e08d24",
"#5588e5",
"#cea339",
"#e27adc",
"#40793c",
"#e653b7",
"#54b28e",
"#e52f66",
"#42c0c7",
"#e03d47",
"#3fa1cc",
"#ba3020",
"#65aae3",
"#e86838",
"#486ca9",
"#dd8d4e",
"#7059a0",
"#b6ac61",
"#944597",
"#747227",
"#b92c81",
"#9a692f",
"#bb86d9",
"#ad5121",
"#9b99dd",
"#b52c49",
"#d7a171",
"#ed4d95",
"#e3897d",
"#a84b85",
"#c85850",
"#e280c0",
"#e95d6e",
"#965e8a",
"#c74172",
"#e199c4",
"#9d3553",
"#d0799e",
"#9f5261",
"#e4748d"};
	
	public RandomColorFactory(){
		colors = new ArrayList<Color>();
	}
	
	public void Reset(){
		currentIndex = 0;
	}
	
	public void advance(){
		this.currentIndex ++;
	}	
	public Color getColor(){
		if(currentIndex < colors.size()){
			Color color = colors.get(currentIndex);
			currentIndex += 1;
			return color;
		}else{
			Color color;
			if(currentIndex < all_standard_colors.length){
				color = Color.web(all_standard_colors[currentIndex]);
			}else{
				color = Color.color(Math.random(), Math.random(), Math.random());
			}
			colors.add(color);
			currentIndex += 1;
			return color;
		}
	}
	
}
