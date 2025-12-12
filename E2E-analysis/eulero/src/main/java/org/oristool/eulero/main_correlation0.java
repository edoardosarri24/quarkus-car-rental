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

public class main_correlation0 {

    public static void main(String[] args) {
        System.err.println("executing the workflow analysis...");

        // Simple activities, the block of our model.

        // users
        Activity usersReserve = new Simple(
            "usersReserve",
            new HyperExponentialTime(
                new BigDecimal(5.330562186693816),
                new BigDecimal(0.17760376739752118),
                new BigDecimal(0.9677562787908376)));
        Activity usersStartParallel = new Simple(
            "usersStartParallel",
            new HyperExponentialTime(
                new BigDecimal(10.720913057426694),
                new BigDecimal(0.11275205859718256),
                new BigDecimal(0.9895924364109785)));
        Activity usersReservation = new Simple(
            "usersReservation",
            new HyperExponentialTime(
                new BigDecimal(8.610101951017985),
                new BigDecimal(0.3659556251618977),
                new BigDecimal(0.9592298041700347)));
        Activity usersReservationAll = new Simple(
            "usersReservationAll",
            new HyperExponentialTime(
                new BigDecimal(9.128382821617187),
                new BigDecimal(0.30916468709284184),
                new BigDecimal(0.9672409927677175)));
        Activity usersEnd = new Simple(
            "usersEnd",
            new HyperExponentialTime(
                new BigDecimal(0.701852467912631),
                new BigDecimal(0.15388314785959686),
                new BigDecimal(0.8201744265128774)));

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
                new BigDecimal(0.9576288589279857),
                new BigDecimal(0.12336204163498625),
                new BigDecimal(0.8858805919913477)));

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
                new BigDecimal(19.983403362938837),
                new BigDecimal(0.6727607892647145),
                new BigDecimal(0.9674305072177234)));
        Activity startParallelEnd = new Simple(
            "startParallelEnd",
            new HyperExponentialTime(
                new BigDecimal(16.665664955018816),
                new BigDecimal(0.18488823758772183),
                new BigDecimal(0.9890277645205829)));

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
                new BigDecimal(1.3434929556854778),
                new BigDecimal(0.16412951805134077),
                new BigDecimal(0.8911335424414797)));

        // reservation
        Activity reservation = new Simple(
            "reservation",
            new HyperExponentialTime(
                new BigDecimal(0.8858306657620005),
                new BigDecimal(0.13015443279114874),
                new BigDecimal(0.8718933644041631)));
        Activity reservationAll = new Simple(
            "reservationAll",
            new HyperExponentialTime(
                new BigDecimal(0.438317998655792),
                new BigDecimal(0.1573271457560151),
                new BigDecimal(0.7358710177829555)));

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