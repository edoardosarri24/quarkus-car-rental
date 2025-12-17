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
                new BigDecimal(3.352469257076943),
                new BigDecimal(3.0270344309393695),
                new BigDecimal(0.5255062808999462)));
        Activity usersStartParallel = new Simple(
            "usersStartParallel",
            new HypoExponentialTime(
                new BigDecimal(6.407353864052392),
                new BigDecimal(45.95974819669674)));
        Activity usersReservation = new Simple(
            "usersReservation",
            new HypoExponentialTime(
                new BigDecimal(0.14356991427736668),
                new BigDecimal(2.753427877788645)));
        Activity usersReservationAll = new Simple(
            "usersReservationAll",
            new HypoExponentialTime(
                new BigDecimal(5.3156996252496285),
                new BigDecimal(12.00445564043343)));
        Activity usersEnd = new Simple(
            "usersEnd",
            new HyperExponentialTime(
                new BigDecimal(0.967379982462932),
                new BigDecimal(0.36153378972685485),
                new BigDecimal(0.7279478945190562)));

        // start-choice
        Activity startChoiceFirstChoice = new Simple(
            "startChoiceFirstChoice",
            new GeneralizeErlangTime(
                2,
                new BigDecimal(8.61178205936351),
                new BigDecimal(4.845183136826742)));
        Activity startChoiceSecondChoice = new Simple(
            "startChoiceSecondChoice",
            new GeneralizeErlangTime(
                3,
                new BigDecimal(11.888800556965649),
                new BigDecimal(5.202992699170525)));
        Activity startChoiceThirdChoice = new Simple(
            "startChoiceThirdChoice",
            new GeneralizeErlangTime(
                2,
                new BigDecimal(8.17852488220188),
                new BigDecimal(5.202992699170525)));
        Activity startChoiceEnd = new Simple(
            "startChoiceEnd",
            new HyperExponentialTime(
                new BigDecimal(10.196299610183832),
                new BigDecimal(1.1449085259744196),
                new BigDecimal(0.8990488039520057)));

        // first-choice
        Activity firstChoice = new Simple(
            "firstChoice",
            new HypoExponentialTime(
                new BigDecimal(0.4992498903823463),
                new BigDecimal(2.0891856639392343)));

        // second-choice
        Activity secondChoice = new Simple(
            "secondChoice",
            new HypoExponentialTime(
                new BigDecimal(0.4329701357329811),
                new BigDecimal(6.94801799693846)));

        // third-choice
        Activity thirdChoice = new Simple(
            "thirdChoice",
            new HypoExponentialTime(
                new BigDecimal(0.4516766301345311),
                new BigDecimal(3.877811148514542)));

        // start-parallel
        Activity startParallel = new Simple(
            "startParallel",
            new GeneralizeErlangTime(
                3,
                new BigDecimal(24.568895226201782),
                new BigDecimal(14.877015265058985)));
        Activity startParallelEnd = new Simple(
            "startParallelEnd",
            new GeneralizeErlangTime(
                2,
                new BigDecimal(0.23215322592265153),
                new BigDecimal(0.05939469383743242)));

        // first-parallel
        Activity firstParallel = new Simple(
            "firstParallel",
            new HypoExponentialTime(
                new BigDecimal(0.09836620229090995),
                new BigDecimal(7.482600884917778)));

        // second-parallel
        Activity secondParallel = new Simple(
            "secondParallel",
            new HypoExponentialTime(
                new BigDecimal(0.06659907802665115),
                new BigDecimal(2.1444332051441597)));

        // reservation
        Activity reservation = new Simple(
            "reservation",
            new GeneralizeErlangTime(
                4,
                new BigDecimal(0.5995779213632655),
                new BigDecimal(0.2593416406972565)));
        Activity reservationAll = new Simple(
            "reservationAll",
            new HypoExponentialTime(
                new BigDecimal(0.6488147177249314),
                new BigDecimal(1.119159779202586)));

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
        double fairTimeLimit = 280;
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