import "stats"

ds := stats.read_csv("reale.csv");
sub := ds.subset(1,1);
sale_p := ds.get_column_by_name("sale price in $100000");
list_p := ds.get_column_by_name("list price in $100000");
lm := new stats.LinearModel(sale_p, list_p);
lm.summary();
