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
import org.oristool.eulero.modeling.stochastictime.ErlangTime;

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
                new BigDecimal(5.7600485656254214),
                new BigDecimal(0.12219263528995943),
                new BigDecimal(0.9792268573973226)));
        Activity usersStartParallel = new Simple(
            "usersStartParallel",
            new HyperExponentialTime(
                new BigDecimal(13.173455351777632),
                new BigDecimal(0.1424628402273945),
                new BigDecimal(0.9893013130470469)));
        Activity usersReservation = new Simple(
            "usersReservation",
            new HyperExponentialTime(
                new BigDecimal(8.64887895058662),
                new BigDecimal(0.35632877003057334),
                new BigDecimal(0.9604308105836618)));
        Activity usersReservationAll = new Simple(
            "usersReservationAll",
            new HyperExponentialTime(
                new BigDecimal(10.049524962359207),
                new BigDecimal(0.2540637883815129),
                new BigDecimal(0.9753422041069673)));
        Activity usersEnd = new Simple(
            "usersEnd",
            new HyperExponentialTime(
                new BigDecimal(0.7018647872684081),
                new BigDecimal(0.18548264294018488),
                new BigDecimal(0.7909695383953694)));

        // start-choice
        Activity startChoiceFirstChoice = new Simple(
            "startChoiceFirstChoice",
            new HypoExponentialTime(
                new BigDecimal(4.410868885967287),
                new BigDecimal(129.2995695422471)));
        Activity startChoiceSecondChoice = new Simple(
            "startChoiceSecondChoice",
            new HyperExponentialTime(
                new BigDecimal(7.752403960497947),
                new BigDecimal(0.4346454089309928),
                new BigDecimal(0.9469106158619256)));
        Activity startChoiceThirdChoice = new Simple(
            "startChoiceThirdChoice",
            new HyperExponentialTime(
                new BigDecimal(6.675905248990738),
                new BigDecimal(0.13470688164846797),
                new BigDecimal(0.9802210316687312)));
        Activity startChoiceEnd = new Simple(
            "startChoiceEnd",
            new HyperExponentialTime(
                new BigDecimal(16.65791760702171),
                new BigDecimal(1.0715247169178783),
                new BigDecimal(0.9395624127742006)));

        // first-choice
        Activity firstChoice = new Simple(
            "firstChoice",
            new HyperExponentialTime(
                new BigDecimal(3.780982996244664),
                new BigDecimal(0.1639459030260373),
                new BigDecimal(0.9584413541505536)));

        // second-choice
        Activity secondChoice = new Simple(
            "secondChoice",
            new HyperExponentialTime(
                new BigDecimal(1.0153966151575535),
                new BigDecimal(0.37879257204204353),
                new BigDecimal(0.7283061900638494)));

        // third-choice
        Activity thirdChoice = new Simple(
            "thirdChoice",
            new HyperExponentialTime(
                new BigDecimal(0.999356388170639),
                new BigDecimal(0.22440411796218557),
                new BigDecimal(0.8166274227370521)));

        // start-parallel
        Activity startParallel = new Simple(
            "startParallel",
            new HyperExponentialTime(
                new BigDecimal(9.798566749814462),
                new BigDecimal(0.7159185398443956),
                new BigDecimal(0.9319112138995038)));
        Activity startParallelEnd = new Simple(
            "startParallelEnd",
            new HyperExponentialTime(
                new BigDecimal(9.765123344130705),
                new BigDecimal(0.05884778847057142),
                new BigDecimal(0.9940097759168609)));

        // first-parallel
        Activity firstParallel = new Simple(
            "firstParallel",
            new HyperExponentialTime(
                new BigDecimal(1.369326708179833),
                new BigDecimal(0.19914222905019568),
                new BigDecimal(0.8730339987466453)));

        // second-parallel
        Activity secondParallel = new Simple(
            "secondParallel",
            new HyperExponentialTime(
                new BigDecimal(9.08433095429603),
                new BigDecimal(0.12159196228323334),
                new BigDecimal(0.9867919856178402)));

        // reservation
        Activity reservation = new Simple(
            "reservation",
            new HyperExponentialTime(
                new BigDecimal(0.986934933297376),
                new BigDecimal(0.20581077674489803),
                new BigDecimal(0.8274479002422037)));
        Activity reservationAll = new Simple(
            "reservationAll",
            new HyperExponentialTime(
                new BigDecimal(0.39112150121807526),
                new BigDecimal(0.15765798045448967),
                new BigDecimal(0.7127115977915552)));

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