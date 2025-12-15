package org.oristool.eulero;

import org.oristool.eulero.modeling.Activity;
import org.oristool.eulero.modeling.ModelFactory;
import org.oristool.eulero.modeling.Simple;
import org.oristool.eulero.evaluation.heuristics.SDFHeuristicsVisitor;
import org.oristool.eulero.evaluation.approximator.TruncatedExponentialMixtureApproximation;
import org.oristool.eulero.evaluation.heuristics.AnalysisHeuristicsVisitor;
import org.oristool.eulero.modeling.stochastictime.HypoExponentialTime;
import org.oristool.eulero.modeling.stochastictime.HyperExponentialTime;
import org.oristool.eulero.modeling.stochastictime.GeneralizeErlangTime;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.List;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.io.IOException;

public class main_high_correlation {

    public static void main(String[] args) {
        System.err.println("executing the workflow analysis...");

        // Simple activities, the block of our model.

        // users
        Activity usersReserve = new Simple(
            "usersReserve",
            new HyperExponentialTime(
                new BigDecimal(4.79585549168319),
                new BigDecimal(1.2031564888439124),
                new BigDecimal(0.7994408924753977)));
        Activity usersStartParallel = new Simple(
            "usersStartParallel",
            new HyperExponentialTime(
                new BigDecimal(9.428850669539896),
                new BigDecimal(0.42922991854977727),
                new BigDecimal(0.9564590779397397)));
        Activity usersReservation = new Simple(
            "usersReservation",
            new HypoExponentialTime(
                new BigDecimal(0.13651165140640883),
                new BigDecimal(3.9321481403796703)));
        Activity usersReservationAll = new Simple(
            "usersReservationAll",
            new HyperExponentialTime(
                new BigDecimal(6.151347322202168),
                new BigDecimal(0.24791295306884648),
                new BigDecimal(0.961259123335416)));
        Activity usersEnd = new Simple(
            "usersEnd",
            new HyperExponentialTime(
                new BigDecimal(0.6564675379852111),
                new BigDecimal(0.5423765566339053),
                new BigDecimal(0.5475837441513)));

        // start-choice
        Activity startChoiceFirstChoice = new Simple(
            "startChoiceFirstChoice",
            new GeneralizeErlangTime(
                3,
                new BigDecimal(12.273343292979211),
                new BigDecimal(4.747338247268098)));
        Activity startChoiceSecondChoice = new Simple(
            "startChoiceSecondChoice",
            new GeneralizeErlangTime(
                5,
                new BigDecimal(16.84328755242238),
                new BigDecimal(7.334855883762797)));
        Activity startChoiceThirdChoice = new Simple(
            "startChoiceThirdChoice",
            new GeneralizeErlangTime(
                3,
                new BigDecimal(12.421996333601232),
                new BigDecimal(4.962445132686599)));
        Activity startChoiceEnd = new Simple(
            "startChoiceEnd",
            new HyperExponentialTime(
                new BigDecimal(7.733611480592421),
                new BigDecimal(3.5000299676342865),
                new BigDecimal(0.6884331778110306)));

        // first-choice
        Activity firstChoice = new Simple(
            "firstChoice",
            new HyperExponentialTime(
                new BigDecimal(0.5995987537964107),
                new BigDecimal(0.1607609321455283),
                new BigDecimal(0.7885725201930235)));

        // second-choice
        Activity secondChoice = new Simple(
            "secondChoice",
            new HypoExponentialTime(
                new BigDecimal(0.4620606198831291),
                new BigDecimal(4.1962931541242385)));

        // third-choice
        Activity thirdChoice = new Simple(
            "thirdChoice",
            new HyperExponentialTime(
                new BigDecimal(0.5093492426348707),
                new BigDecimal(0.2981636156583076),
                new BigDecimal(0.6307630118874772)));

        // start-parallel
        Activity startParallel = new Simple(
            "startParallel",
            new HypoExponentialTime(
                new BigDecimal(0.197524712683633),
                new BigDecimal(9.137586429172682)));
        Activity startParallelEnd = new Simple(
            "startParallelEnd",
            new HypoExponentialTime(
                new BigDecimal(0.3271061538115266),
                new BigDecimal(0.9559339396215777)));

        // first-parallel
        Activity firstParallel = new Simple(
            "firstParallel",
            new HyperExponentialTime(
                new BigDecimal(0.6010410170555895),
                new BigDecimal(0.2898943273189144),
                new BigDecimal(0.6746179965253937)));

        // second-parallel
        Activity secondParallel = new Simple(
            "secondParallel",
            new HyperExponentialTime(
                new BigDecimal(0.6059149545859117),
                new BigDecimal(0.2917261821435134),
                new BigDecimal(0.6750080068673946)));

        // reservation
        Activity reservation = new Simple(
            "reservation",
            new GeneralizeErlangTime(
                3,
                new BigDecimal(0.4637518135266925),
                new BigDecimal(0.24031367819762137)));
        Activity reservationAll = new Simple(
            "reservationAll",
            new GeneralizeErlangTime(
                2,
                new BigDecimal(2.1276535315696776),
                new BigDecimal(0.5810213732194183)));

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
        // double fairTimeLimit = model.getFairTimeLimit();
        double fairTimeLimit = 206;
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