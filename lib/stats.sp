import "math"
import "io"
import "functions"

class DataSet {
    var rows;  // List

    fn DataSet(lst=null) {
        this.rows = lst;
    }

    fn get_column(index) {
        lst := [];
        for var row; rows {
            lst.append(row[index]);
        }
        return lst;
    }

    fn get_column_by_name(name) {
        for i := 0; i < rows[0].size(); i++ {
            if rows[0][i] == name {
                return get_column(i).sublist(1);
            }
        }
        return null;
    }

    fn subset(from_row, from_col, to_row=null, to_col=null) {
        if to_row === null {
            to_row = rows.size();
        }
        if to_col === null {
            to_col = rows[0].size();
        }
        lst := [];
        for i := from_row; i < to_row; i++ {
            lst.append(rows[i].sublist(from_col, to_col));
        }
        return new DataSet(lst);
    }

    fn __str__() {
        return string(rows);
    }
}

class LinearModel {
    var intercept;
    var slope;
    var correlation;
    var r_squared;
    var rss;  // Residual squared error
    var rse;  // Residual standard error
    var df;

    fn LinearModel(y_data, x_data) {
        assert y_data.size() == x_data.size();
        x_mean := mean(x_data);
        y_mean := mean(y_data);
        n := x_data.size();
        df = n - 2;
        sxx := 0;
        sxy := 0;
        syy := 0;
        for i := 0; i < n; i++ {
            sxx += math.pow(x_data[i] - x_mean, 2);
            sxy += (x_data[i] - x_mean) * (y_data[i] - y_mean);
            s_res := math.pow(y_data[i] - y_mean, 2);
            syy += s_res;
        }

        slope = float(sxy) / sxx;
        intercept = y_mean - slope * x_mean;
        correlation = sxy / math.sqrt(sxx * syy);
        r_squared = math.pow(correlation, 2);

        rss = 0;

        for i := 0; i < n; i++ {
            predict := intercept + slope * x_data[i];
            residual := y_data[i] - predict;
            rss += math.pow(residual, 2);
        }
        rse = math.sqrt(rss / df);
    }

    fn summary() {
        println("Coefficients:");
        println("Intercept %f".format(intercept));
        println("Slope     %f".format(slope));
        println("Multiple R-squared: %4f".format(r_squared));
        println("Residual standard error: %4f on %d degrees of freedom".format(rse, df));
    }
}

fn mean(lst) {
    return float(functions.sum(lst)) / lst.size();
}

fn read_csv(file_name) {
    tis := new io.TextInputStream(file_name);
    lst := [];
    var line;
    while line = tis.readline() {
        seg := new List(*line.split(","));
        for i := 0; i < seg.size(); i++ {
            if (seg[i].is_number()) {
                seg[i] = float(seg[i]);
            }
        }
        lst.append(seg);
    }
    return new DataSet(lst);
}

fn slr() {

}
