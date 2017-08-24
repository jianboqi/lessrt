package less.gui.utils;

import javafx.scene.paint.Color;
import less.gui.model.OpticalThermalProperty;

public class CommonUitls {
	public static boolean isNumeric(String str)
	{
	  return str.matches("-?\\d+(\\.\\d+)?");  //match a number with optional '-' and decimal.
	}
	
	/**
	 * 判断一个字符串是否含有与branch有关的名字
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
