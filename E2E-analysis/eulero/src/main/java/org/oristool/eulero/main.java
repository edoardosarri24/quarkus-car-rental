package org.oristool.eulero;

import org.oristool.eulero.modeling.Activity;
import org.oristool.eulero.modeling.ModelFactory;
import org.oristool.eulero.modeling.Simple;
import org.oristool.eulero.modeling.stochastictime.UniformTime;
import org.oristool.eulero.evaluation.heuristics.SDFHeuristicsVisitor;
import org.oristool.eulero.evaluation.approximator.TruncatedExponentialMixtureApproximation;
import org.oristool.eulero.evaluation.heuristics.AnalysisHeuristicsVisitor;
import org.oristool.eulero.ui.ActivityViewer;
import org.oristool.eulero.evaluation.heuristics.EvaluationResult;
import org.oristool.eulero.modeling.stochastictime.HypoExponentialTime;
import org.oristool.eulero.modeling.stochastictime.HyperExponentialTime;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.List;

public class main {

    public static void main(String[] args) {

        System.err.println("executing the workflow analysis...");

        // Simple activities, the block of our model.
        Activity usersReserve = new Simple(
            "usersReserve",
            new HypoExponentialTime(
                BigDecimal.valueOf(0.0343),
                BigDecimal.valueOf(1.1294)));
        Activity startChoice = new Simple(
            "startChoice",
            new HyperExponentialTime(
                BigDecimal.valueOf(0.2426),
                BigDecimal.valueOf(0.0198),
                BigDecimal.valueOf(0.9246)));
        Activity firstChoice = new Simple(
            "firstChoice",
            new HyperExponentialTime(
                BigDecimal.valueOf(0.8041),
                BigDecimal.valueOf(0.0672),
                BigDecimal.valueOf(0.9229)));
        Activity secondChoice = new Simple(
            "secondChoice",
            new HyperExponentialTime(
                BigDecimal.valueOf(0.8021),
                BigDecimal.valueOf(0.1318),
                BigDecimal.valueOf(0.8530)));
        Activity thirdChoice = new Simple(
            "thirdChoice",
            new HyperExponentialTime(
                BigDecimal.valueOf(0.7874),
                BigDecimal.valueOf(0.0989),
                BigDecimal.valueOf(0.8884)));
        Activity usersParallel = new Simple(
            "usersParallel",
            new HyperExponentialTime(
                BigDecimal.valueOf(0.2933),
                BigDecimal.valueOf(0.0754),
                BigDecimal.valueOf(0.7955)));
        Activity startParallel = new Simple(
            "startParallel",
            new HyperExponentialTime(
                BigDecimal.valueOf(0.1368),
                BigDecimal.valueOf(0.0331),
                BigDecimal.valueOf(0.8050)));
        Activity firstParallel = new Simple(
            "firstParallel",
            new HyperExponentialTime(
                BigDecimal.valueOf(0.8916),
                BigDecimal.valueOf(0.0825),
                BigDecimal.valueOf(0.9153)));
        Activity secondParallel = new Simple(
            "secondParallel",
            new HyperExponentialTime(
                BigDecimal.valueOf(0.9210),
                BigDecimal.valueOf(0.1019),
                BigDecimal.valueOf(0.9004)));
        Activity usersReservation = new Simple(
            "usersReservation",
            new HyperExponentialTime(
                BigDecimal.valueOf(0.4417),
                BigDecimal.valueOf(0.0721),
                BigDecimal.valueOf(0.8596)));
        Activity reservationReservation = new Simple(
            "reservationReservation",
            new HyperExponentialTime(
                BigDecimal.valueOf(0.4447),
                BigDecimal.valueOf(0.0526),
                BigDecimal.valueOf(0.8942)));
        Activity usersReservationAll = new Simple(
            "usersReservationAll",
            new HyperExponentialTime(
                BigDecimal.valueOf(0.2858),
                BigDecimal.valueOf(0.0974),
                BigDecimal.valueOf(0.7459)));
        Activity reservationReservationAll = new Simple(
            "reservationReservationAll",
            new HyperExponentialTime(
                BigDecimal.valueOf(0.2833),
                BigDecimal.valueOf(0.0637),
                BigDecimal.valueOf(0.8165)));

        // Model of the workflow.
        Activity model = ModelFactory.sequence(
            usersReserve,
            startChoice,
            ModelFactory.XOR(List.of(0.2, 0.5, 0.3), firstChoice, secondChoice, thirdChoice),
            usersParallel,
            ModelFactory.forkJoin(firstParallel, secondParallel),
            usersReservation,
            reservationReservation,
            usersReservationAll,
            reservationReservationAll
        );

        // Analyze the model.
        AnalysisHeuristicsVisitor analyzer = new SDFHeuristicsVisitor(
            BigInteger.valueOf(2),
            BigInteger.valueOf(5),
            new TruncatedExponentialMixtureApproximation());
        double fairTimeTick = model.getLeastExpectedTimeTick();
        BigDecimal timeStep = BigDecimal.valueOf(fairTimeTick);
        //double fairTimeLimit = model.getFairTimeLimit();
        double fairTimeLimit = 500;
        double[] cdf = model.analyze(BigDecimal.valueOf(fairTimeLimit), timeStep, analyzer);

        // show the result
        EvaluationResult result = new EvaluationResult("E2E workflow analysis", cdf, 0, cdf.length, timeStep.doubleValue(), 0);
        ActivityViewer.CompareResults("../", true, "E2E workflow analysis", List.of("CFD"), result);
    }

}