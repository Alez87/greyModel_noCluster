/*
 * Created on 20-lug-2005
 *
 * To change the template for this generated file go to
 * Window&gt;Preferences&gt;Java&gt;Code Generation&gt;Code and Comments
 */
package py4j;

import java.util.ArrayList;
import Jama.Matrix;
import py4j.GatewayServer;

public class Grey implements IFilter{
	
	public IFilter genFilter(){
		return new Grey();
	}
	// Costruisco il Grey model GM(1,1) ed effettuo la predizione.
	// (questo metodo effettua operazioni algebriche con matrci 2*n;
	// vi consiglio di prenderlo per buono cosi com'e!)
	public Double nextValue(ArrayList<Double> valueSet){//, double costante){
		int costante=0;
		// Il valore "costante", aggiunta in X1, serve a rendere le previsioni piu gradua
		// Infatti quando le previsioni vengono fatte su numeri piccoli, basta una piccola variazioni
		// per ottenere una predizione a picco. Aggiungendo una costante le predizioni dovrebbero essere
		// piu regolari e simili con valori grandi e piccoli.
		
		// Se ci sono meno di 4 valori, non e possibile creare GM(1,1)
		// e restituisco il valore misurato.
		if (valueSet.size()<4){
			if(valueSet.size()==0){
				return null;
			}
			return valueSet.get(valueSet.size() - 1);
		}
		
		// costruisco X1
		double[][] valX1=new double[1][valueSet.size()]; // 1 riga, n colonne
		for(int i=0;i<valueSet.size();i++){
			double xi=0;
			for(int a=0;a<=i;a++){
				if(valueSet.get(a)==null)return null;
				xi=xi+(((Double)valueSet.get(a)).doubleValue()+costante);
			}
			valX1[0][i]=xi; // riga 1, colonna i
		}
		//System.out.print("X1 ");
		Matrix X1=new Matrix(valX1);
		//X1.print(1,valori.size());
		/*Vector X1=new Vector();
		for(int i=0;i<valori.size();i++){
			double xi=0;
			for(int a=0;a<=i;a++){
				if(valori.elementAt(a)==null)return null;
				xi=xi+(((Double)valori.elementAt(a)).doubleValue()+costante);
			}
			X1.addElement(new Double(xi));
		}*/
		
		// costruisco B
		//double[][] valB=new double[2][valori.size()-1];
		double[][] valB=new double[valueSet.size()-1][2];
		for(int x=0;x<valueSet.size()-1;x++){
			valB[x][0]=-0.5*(X1.get(0,x)+X1.get(0,x+1));
			valB[x][1]=1;
		}
		Matrix B=new Matrix(valB);
		//System.out.print("B ");
		//B.print(2,valori.size()-1);
		/*Vector B=new Vector();
		for(int x=0;x<valori.size()-1;x++){
			Vector rigax=new Vector();
			rigax.addElement(new Double(-0.5*(((Double)X1.elementAt(x)).doubleValue()+((Double)X1.elementAt(x+1)).doubleValue())));
			rigax.addElement(new Double(1));
			B.addElement(rigax);
		}*/
		
		// costruisco B trasposta
		Matrix Bt=B.transpose();
		//System.out.print("Bt ");
		//Bt.print(valori.size()-1,2);
		/*Vector Bt=new Vector();
		Vector riga1Bt=new Vector();
		for(int x=0;x<valori.size()-1;x++){
			riga1Bt.addElement(new Double(-0.5*(((Double)X1.elementAt(x)).doubleValue()+((Double)X1.elementAt(x+1)).doubleValue())));
		}
		Vector riga2Bt=new Vector();
		for(int x=0;x<valori.size()-1;x++){
			riga2Bt.addElement(new Double(1));
		}
		Bt.addElement(riga1Bt);
		Bt.addElement(riga2Bt);*/
		
		
		// calcolo il prodotto tra B trasposta e B (BtB)
		Matrix BtB=Bt.times(B);
		//System.out.print("BtB ");
		//BtB.print(2,2);
		//BtB.print(valori.size()-1,valori.size()-1);
		/*Vector BtB=new Vector();
		
		// riga 1 di BtB
		Vector riga1BtB=new Vector();
		double somm=0;
		for(int x=0;x<valori.size()-1;x++){
			double c=((Double)riga1Bt.elementAt(x)).doubleValue();
			Vector rigax=(Vector)B.elementAt(x);
			double d=((Double)rigax.elementAt(0)).doubleValue();
			somm=somm+(c*d);
		}
		riga1BtB.addElement(new Double(somm));
		somm=0;
		for(int x=0;x<valori.size()-1;x++){
			double c=((Double)riga1Bt.elementAt(x)).doubleValue();
			Vector rigax=(Vector)B.elementAt(x);
			double d=((Double)rigax.elementAt(1)).doubleValue();
			somm=somm+(c*d);
		}
		riga1BtB.addElement(new Double(somm));
		BtB.addElement(riga1BtB);
		
		// riga 2 di BtB
		Vector riga2BtB=new Vector();
		somm=0;
		for(int x=0;x<valori.size()-1;x++){
			double c=((Double)riga2Bt.elementAt(x)).doubleValue();
			Vector rigax=(Vector)B.elementAt(x);
			double d=((Double)rigax.elementAt(0)).doubleValue();
			somm=somm+(c*d);
		}
		riga2BtB.addElement(new Double(somm));
		somm=0;
		for(int x=0;x<valori.size()-1;x++){
			double c=((Double)riga2Bt.elementAt(x)).doubleValue();
			Vector rigax=(Vector)B.elementAt(x);
			double d=((Double)rigax.elementAt(1)).doubleValue();
			somm=somm+(c*d);
		}
		riga2BtB.addElement(new Double(somm));
		BtB.addElement(riga2BtB);
		double a=((Double)riga1BtB.elementAt(0)).doubleValue();
		double b=((Double)riga1BtB.elementAt(1)).doubleValue();
		double c=((Double)riga2BtB.elementAt(0)).doubleValue();
		double d=((Double)riga2BtB.elementAt(1)).doubleValue();*/
		
		// calcolo il determinante di BtB (det)
		// double det=BtB.det();
		// double det=a*d-b*c;
		
		// costruisco l'inversa di BtB (BtB_1)
		Matrix BtB_1=BtB.inverse();
		//System.out.print("BtB_1 ");
		//BtB_1.print(2,2);
		/*Vector BtB_1=new Vector();
		Vector riga1BtB_1=new Vector();
		riga1BtB_1.addElement(new Double(d/det));
		riga1BtB_1.addElement(new Double((-b)/det));
		Vector riga2BtB_1=new Vector();
		riga2BtB_1.addElement(new Double((-c)/det));
		riga2BtB_1.addElement(new Double(a/det));
		BtB_1.addElement(riga1BtB_1);
		BtB_1.addElement(riga2BtB_1);
		double a1=d/det;
		double b1=(-b)/det;
		double c1=(-c)/det;
		double d1=a/det;*/
		
		// calcolo il prodotto tra BtB_1 e Bt (C)
		Matrix C=BtB_1.times(Bt);
		//System.out.print("C ");
		//C.print(3,3);
		/*Vector C=new Vector();
		Vector riga1C=new Vector();
		for(int q=0;q<riga1Bt.size();q++){
			double g=a1*((Double)riga1Bt.elementAt(q)).doubleValue();
			double h=b1*((Double)riga2Bt.elementAt(q)).doubleValue();
			riga1C.addElement(new Double(g+h));
		}
		C.addElement(riga1C);
		Vector riga2C=new Vector();
		for(int q=0;q<riga1Bt.size();q++){
			double g=c1*((Double)riga1Bt.elementAt(q)).doubleValue();
			double h=d1*((Double)riga2Bt.elementAt(q)).doubleValue();
			riga2C.addElement(new Double(g+h));
		}
		C.addElement(riga2C);*/

		// costruisco Yn
		double[][] valYn=new double[valueSet.size()-1][1];
		for(int i=1;i<valueSet.size();i++){
			valYn[i-1][0]=valueSet.get(i); // riga 1, colonna i
		}
		Matrix Yn=new Matrix(valYn);
		//System.out.print("Yn ");
		//Yn.print(2,2);
		
		// calcolo a_ ed u
		Matrix au=C.times(Yn);
		//System.out.print("au");
		//au.print(2,2);
		/*double a_=0;
		for(int q=0;q<riga1C.size();q++){
			double aggiunta=( ((Double)riga1C.elementAt(q)).doubleValue() * (((Double)valori.elementAt(q+1)).doubleValue()+costante) );
			a_=a_+aggiunta;
		}
		double u=0;
		for(int q=0;q<riga2C.size();q++){
			u=u+( ((Double)riga2C.elementAt(q)).doubleValue() * (((Double)valori.elementAt(q+1)).doubleValue()+costante ));
		}*/
		
		// richiedo la predizione
		double ris1=x1_(valueSet.size()+1,au.get(0,0),au.get(1,0),X1.get(0,0));
		double ris2=x1_(valueSet.size(),au.get(0,0),au.get(1,0),X1.get(0,0));
		/*double ris1=x1_(valori.size()+1,a_,u,((Double)X1.elementAt(0)).floatValue());
		double ris2=x1_(valori.size(),a_,u,((Double)X1.elementAt(0)).floatValue());*/
		
		//double risultato=ris1-ris2;
		return new Double(ris1-ris2-costante);
	}
	
	private double x1_(int k,double a,double u,double x1){
		// prova ad eliminare
		// Per problemi di arrotondamento nell'esponenziazione,
		// impongo un valore minimo ad a.
		if(a<0&&a>-0.000000000001)a=-0.000000000001;
		if(a>=0&&a<0.000000000001)a=0.000000000001;
		
		// effettuo la predizione
		double x1_=(x1-u/a)*Math.exp((-a)*(double)k);
		return x1_;
	}
	
	 public static void main(String[] args) {
        GatewayServer gatewayServer = new GatewayServer(new Grey());
        gatewayServer.start();
        System.out.println("Gateway Server Started");
    }
}
