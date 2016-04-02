/*
 * Created on 21-lug-2005
 *
 * To change the template for this generated file go to
 * Window&gt;Preferences&gt;Java&gt;Code Generation&gt;Code and Comments
 */
package py4j;

import java.util.ArrayList;

public interface IFilter {
	// valori: sequenza di valori di cui effettuare la predizione/il filtraggio
	// costante: di norma settato a zero, serve a Grey per non avere valori vicini a zero
	public Double nextValue(ArrayList<Double> valueSet);//, double costante);
	public IFilter genFilter();
}
