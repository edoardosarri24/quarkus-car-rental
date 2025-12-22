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
            new GeneralizeErlangTime(
                2,
                new BigDecimal(19.41906229285001),
                new BigDecimal(5.2721871632240305)));
        Activity usersStartParallel = new Simple(
            "usersStartParallel",
            new HypoExponentialTime(
                new BigDecimal(8.355721262813686),
                new BigDecimal(23.33730263755574)));
        Activity usersReservation = new Simple(
            "usersReservation",
            new GeneralizeErlangTime(
                2,
                new BigDecimal(17.264868410029777),
                new BigDecimal(6.182247384787136)));
        Activity usersReservationAll = new Simple(
            "usersReservationAll",
            new GeneralizeErlangTime(
                2,
                new BigDecimal(18.40653910419777),
                new BigDecimal(9.09950806433991)));
        Activity usersEnd = new Simple(
            "usersEnd",
            new HypoExponentialTime(
                new BigDecimal(0.6658598204112933),
                new BigDecimal(1.9739367996142911)));

        // start-choice
        Activity startChoiceFirstChoice = new Simple(
            "startChoiceFirstChoice",
            new GeneralizeErlangTime(10, new BigDecimal(32.020722081948854), new BigDecimal(15.80410969408365)));
        Activity startChoiceSecondChoice = new Simple(
            "startChoiceSecondChoice",
            new HyperExponentialTime(new BigDecimal(3.718284308783372), new BigDecimal(1.0346753541423916), new BigDecimal(0.7823092499157714)));
        Activity startChoiceThirdChoice = new Simple(
            "startChoiceThirdChoice",
            new GeneralizeErlangTime(
                9,
                new BigDecimal(28.53283557000774),
                new BigDecimal(16.350741815789924)));
        Activity startChoiceEnd = new Simple(
            "startChoiceEnd",
            new GeneralizeErlangTime(
                6,
                new BigDecimal(54.66581888796796),
                new BigDecimal(23.931933379127155)));

        // first-choice
        Activity firstChoice = new Simple(
            "firstChoice",
            new HypoExponentialTime(new BigDecimal(0.5066779773759286), new BigDecimal(2.054014045256548)));

        // second-choice
        Activity secondChoice = new Simple(
            "secondChoice",
            new HyperExponentialTime(new BigDecimal(0.5406059054709982), new BigDecimal(0.3469190334132792), new BigDecimal(0.6091162983550671)));

        // third-choice
        Activity thirdChoice = new Simple(
            "thirdChoice",
            new HyperExponentialTime(new BigDecimal(0.5285179603753328), new BigDecimal(0.25916687581850056), new BigDecimal(0.6709764312960256)));

        // start-parallel
        Activity startParallel = new Simple(
            "startParallel",
            new HyperExponentialTime(new BigDecimal(0.5355212665163307), new BigDecimal(0.32935722426912195), new BigDecimal(0.6191867091410597)));
        Activity startParallelEnd = new Simple(
            "startParallelEnd",
            new GeneralizeErlangTime(
                8,
                new BigDecimal(76.15894832084263),
                new BigDecimal(64.72371240891827)));

        // first-parallel
        Activity firstParallel = new Simple(
            "firstParallel",
            new HyperExponentialTime(
                new BigDecimal(0.6445899927541169),
                new BigDecimal(0.2608245560127369),
                new BigDecimal(0.7119280263742483)));

        // second-parallel
        Activity secondParallel = new Simple(
            "secondParallel",
            new HyperExponentialTime(
                new BigDecimal(0.6226877588686539),
                new BigDecimal(0.23052228234611083),
                new BigDecimal(0.7298176636342643)));

        // reservation
        Activity reservation = new Simple(
            "reservation",
            new HypoExponentialTime(new BigDecimal(0.8419123392111378), new BigDecimal(2.2588156136721516)));
        Activity reservationAll = new Simple(
            "reservationAll",
            new HypoExponentialTime(new BigDecimal(0.34115331884833233), new BigDecimal(6.780497616257382)));

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
        double fairTimeLimit = 74;
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