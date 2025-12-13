package org.oristool.eulero;

import org.oristool.eulero.modeling.Activity;
import org.oristool.eulero.modeling.ModelFactory;
import org.oristool.eulero.modeling.Simple;
import org.oristool.eulero.modeling.stochastictime.UniformTime;
import org.oristool.eulero.evaluation.heuristics.SDFHeuristicsVisitor;
import org.checkerframework.checker.units.qual.kN;
import org.oristool.eulero.evaluation.approximator.TruncatedExponentialMixtureApproximation;
import org.oristool.eulero.evaluation.heuristics.AnalysisHeuristicsVisitor;
import org.oristool.eulero.ui.ActivityViewer;
import org.oristool.eulero.evaluation.heuristics.EvaluationResult;
import org.oristool.eulero.modeling.stochastictime.HypoExponentialTime;
import org.oristool.eulero.modeling.stochastictime.HyperExponentialTime;
import org.oristool.eulero.modeling.stochastictime.ErlangTime;
import org.oristool.eulero.modeling.stochastictime.GeneralizeErlangTime;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.List;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.io.IOException;

public class main {

    public static void main(String[] args) {
        System.err.println("executing the workflow analysis...");

        // Simple activities, the block of our model.

        // users
        Activity usersReserve = new Simple(
            "usersReserve",
            new HyperExponentialTime(
                new BigDecimal(5.432496539867112),
                new BigDecimal(1.0019698829633752),
                new BigDecimal(0.8442808125615155)));
        Activity usersStartParallel = new Simple(
            "usersStartParallel",
            new HypoExponentialTime(
                new BigDecimal(8.883101076243136),
                new BigDecimal(16.220292860720797)));
        Activity usersReservation = new Simple(
            "usersReservation",
            new HypoExponentialTime(
                new BigDecimal(0.13583779809146426),
                new BigDecimal(4.512163001532629)));
        Activity usersReservationAll = new Simple(
            "usersReservationAll",
            new GeneralizeErlangTime(
                2,
                new BigDecimal(19.43049443858759),
                new BigDecimal(5.744223513812113)));
        Activity usersEnd = new Simple(
            "usersEnd",
            new HypoExponentialTime(
                new BigDecimal(0.8475476358275391),
                new BigDecimal(5.150165626715587)));

        // start-choice
        Activity startChoiceFirstChoice = new Simple(
            "startChoiceFirstChoice",
            new HypoExponentialTime(
                new BigDecimal(3.5201746455002234),
                new BigDecimal(6.07269615583936)));
        Activity startChoiceSecondChoice = new Simple(
            "startChoiceSecondChoice",
            new HyperExponentialTime(
                new BigDecimal(3.4733294219152056),
                new BigDecimal(0.8989381939761423),
                new BigDecimal(0.7944000063699483)));
        Activity startChoiceThirdChoice = new Simple(
            "startChoiceThirdChoice",
            new GeneralizeErlangTime(
                4,
                new BigDecimal(12.84080332064955),
                new BigDecimal(8.069272354898319)));
        Activity startChoiceEnd = new Simple(
            "startChoiceEnd",
            new GeneralizeErlangTime(
                2,
                new BigDecimal(29.371489546338974),
                new BigDecimal(9.625590994998777)));

        // first-choice
        Activity firstChoice = new Simple(
            "firstChoice",
            new HypoExponentialTime(
                new BigDecimal(0.44510088082123495),
                new BigDecimal(4.277488383708342)));

        // second-choice
        Activity secondChoice = new Simple(
            "secondChoice",
            new HypoExponentialTime(
                new BigDecimal(0.5402484688380129),
                new BigDecimal(2.0623351589340433)));

        // third-choice
        Activity thirdChoice = new Simple(
            "thirdChoice",
            new HypoExponentialTime(
                new BigDecimal(0.48591912893009037),
                new BigDecimal(2.059133464514165)));

        // start-parallel
        Activity startParallel = new Simple(
            "startParallel",
            new HypoExponentialTime(
                new BigDecimal(0.18877847753595525),
                new BigDecimal(27.504868815828875)));
        Activity startParallelEnd = new Simple(
            "startParallelEnd",
            new HyperExponentialTime(
                new BigDecimal(13.872778574741679),
                new BigDecimal(0.37187136385113845),
                new BigDecimal(0.9738939626137366)));

        // first-parallel
        Activity firstParallel = new Simple(
            "firstParallel",
            new HyperExponentialTime(
                new BigDecimal(0.5281523048770601),
                new BigDecimal(0.37532264121668635),
                new BigDecimal(0.5845788056000591)));

        // second-parallel
        Activity secondParallel = new Simple(
            "secondParallel",
            new HypoExponentialTime(
                new BigDecimal(0.46720863302310595),
                new BigDecimal(13.54958199926677)));

        // reservation
        Activity reservation = new Simple(
            "reservation",
            new GeneralizeErlangTime(
                4,
                new BigDecimal(0.6158220548999678),
                new BigDecimal(0.24688934216814792)));
        Activity reservationAll = new Simple(
            "reservationAll",
            new HypoExponentialTime(
                new BigDecimal(0.7009731271010903),
                new BigDecimal(1.2164000432879931)));

        // Model of the workflow.
        Activity model = ModelFactory.sequence(
            usersReserve,
            ModelFactory.XOR(List.of(0.2, 0.5, 0.3),
                ModelFactory.sequence(startChoiceFirstChoice, firstChoice),
                ModelFactory.sequence(startChoiceSecondChoice, secondChoice),
                ModelFactory.sequence(startChoiceThirdChoice, thirdChoice)),
            startChoiceEnd,
            usersStartParallel,
            startParallel,
            ModelFactory.forkJoin(firstParallel, secondParallel),
            startParallelEnd,
            usersReservation,
            reservation,
            usersReservationAll,
            reservationAll,
            usersEnd
        );

        // Analyze the model.
        AnalysisHeuristicsVisitor analyzer = new SDFHeuristicsVisitor(
            BigInteger.valueOf(2),
            BigInteger.valueOf(5),
            new TruncatedExponentialMixtureApproximation());
        double fairTimeTick = model.getLeastExpectedTimeTick();
        BigDecimal timeStep = BigDecimal.valueOf(fairTimeTick);
        //double fairTimeLimit = model.getFairTimeLimit();
        double fairTimeLimit = 170;
        double[] cdf = model.analyze(BigDecimal.valueOf(fairTimeLimit), timeStep, analyzer);

        // Save cdf to a CSV file
        try (PrintWriter writer = new PrintWriter(new FileWriter("../eulero_CDF.csv"))) {
            writer.println("time,cdf");
            for (int i = 0; i < cdf.length; i++) {
                double time = i * timeStep.doubleValue();
                writer.println(time + "," + cdf[i]);
            }
            System.out.println("CDF saved");
        } catch (IOException e) {
            e.printStackTrace();
        }

    }

}