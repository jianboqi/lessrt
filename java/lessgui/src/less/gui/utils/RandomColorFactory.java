package less.gui.utils;

import java.util.ArrayList;

import javax.xml.stream.events.StartDocument;

import javafx.scene.paint.Color;

public class RandomColorFactory {
	private int currentIndex = 0;
	private ArrayList<Color> colors;
	
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
			Color color = Color.color(Math.random(), Math.random(), Math.random());
			colors.add(color);
			currentIndex += 1;
			return color;
		}
	}
	
}
