package less.gui.utils;

import javafx.scene.paint.Color;
import less.gui.model.OpticalThermalProperty;

public class CommonUitls {
	public static boolean isNumeric(String str)
	{
	  return str.matches("-?\\d+(\\.\\d+)?");  //match a number with optional '-' and decimal.
	}
	
	/**
	 * Check if a string constains "branch" "trunk"
	 * @param str
	 * @return
	 */
	public static boolean contain_branch_names(String str){
		if(str.contains("Branch")||
		   str.contains("Bough")||
		   str.contains("Trunk")){
				return true;
	    }else{
	    	return false;
	    }
	}
}
